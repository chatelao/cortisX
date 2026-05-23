import json
import os
import asyncio
from rdkit import Chem
from rdkit.Chem import AllChem
from playwright.async_api import async_playwright
from PIL import Image
import re

async def render_molecule(page, smiles, name, output_dir):
    """Renders 2D and 3D ball-and-stick assets for a molecule."""
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        print(f"Failed to parse SMILES for {name}")
        return

    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    if AllChem.EmbedMolecule(mol, params) == -1:
        print(f"Failed to generate 3D coordinates for {name}")
        return

    mol_block = Chem.MolToMolBlock(mol)

    # 3Dmol.js Ball-and-Stick Style
    style = "{stick: {radius: 0.15}, sphere: {radius: 0.4}}"

    html_content = f"""
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.4.2/3Dmol-min.js"></script>
    </head>
    <body style="margin:0; padding:0; background-color: white;">
        <div id="container" style="width: 400px; height: 400px;"></div>
        <script>
            let element = document.getElementById('container');
            let viewer = $3Dmol.createViewer(element, {{ backgroundColor: 'white' }});
            viewer.addModel(`{mol_block}`, "mol");
            viewer.setStyle({{}}, {style});
            viewer.zoomTo();
            viewer.rotate(20, 'x');
            viewer.rotate(20, 'y');
            viewer.render();

            window.rotateAndRender = function(angle) {{
                viewer.rotate(angle, 'y');
                viewer.render();
            }};
            window.renderComplete = true;
        </script>
    </body>
    </html>
    """

    # Use a temporary file for rendering
    temp_html = f"temp_{name}.html"
    with open(temp_html, "w") as f:
        f.write(html_content)

    await page.goto(f"file://{os.path.abspath(temp_html)}")
    await page.wait_for_function("window.renderComplete === true")

    # Static 2D Ball-and-Stick
    path_2d = os.path.join(output_dir, f"{name.lower()}_2d.png")
    await page.locator("#container").screenshot(path=path_2d)
    print(f"Generated 2D ball-and-stick for {name}")

    # 3D Animation
    path_anim = os.path.join(output_dir, f"{name.lower()}_animation.gif")
    num_frames = 20
    angle_step = 360 / num_frames
    frames = []

    for i in range(num_frames):
        frame_path = f"temp_frame_{name}_{i}.png"
        await page.evaluate(f"window.rotateAndRender({angle_step})")
        await page.locator("#container").screenshot(path=frame_path)
        frames.append(Image.open(frame_path))

    if frames:
        frames[0].save(
            path_anim,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )
        for img in frames:
            img.close()
        print(f"Generated 3D animation for {name}")

    # Cleanup
    if os.path.exists(temp_html):
        os.remove(temp_html)
    for i in range(num_frames):
        frame_path = f"temp_frame_{name}_{i}.png"
        if os.path.exists(frame_path):
            os.remove(frame_path)

async def main():
    data_path = 'steroids/data.json'
    if not os.path.exists(data_path):
        print(f"Data file not found: {data_path}")
        return

    with open(data_path, 'r') as f:
        data = json.load(f)

    output_dir = 'steroids/images'
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for name, info in data.items():
            await render_molecule(page, info['smiles'], name, output_dir)

        await browser.close()

    # Generate STEROIDS.md in root
    md_content = "# Körpereigene Steroide\n\n"
    md_content += "Diese Übersicht zeigt die wichtigsten körpereigenen Steroide als Kugel-Stäbchenmodelle.\n\n"

    md_content += "| Name | Formel | Gewicht (g/mol) | 2D Modell | 3D Animation |\n"
    md_content += "| :--- | :--- | :--- | :--- | :--- |\n"

    for name, info in data.items():
        formula = info['molecular_formula']
        formatted_formula = re.sub(r'(\d+)', r'<sub>\1</sub>', formula)

        img_2d = f"steroids/images/{name.lower()}_2d.png"
        img_anim = f"steroids/images/{name.lower()}_animation.gif"

        md_content += f"| {name} | {formatted_formula} | {info['molecular_weight']} | ![{name} 2D]({img_2d}) | ![{name} 3D]({img_anim}) |\n"

    with open('STEROIDS.md', 'w') as f:
        f.write(md_content)
    print("Generated STEROIDS.md in root")

if __name__ == "__main__":
    asyncio.run(main())
