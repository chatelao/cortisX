import json
import os
import asyncio
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem
from rdkit.Chem import rdMolTransforms
from rdkit.Chem.Draw import MolDraw2DCairo
import numpy as np
from playwright.async_api import async_playwright
from PIL import Image

def render_2d(smiles, output_path):
    """Generates a 2D PNG image from a SMILES string."""
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        Draw.MolToFile(mol, output_path, size=(400, 400))
        return True
    return False

def render_3d(smiles, output_path):
    """Generates a pseudo-3D PNG image from a SMILES string using RDKit's 3D conformation."""
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return False

    # Add hydrogens and generate 3D conformation
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    if AllChem.EmbedMolecule(mol, params) == -1:
        return False

    # Rotate 180 degrees around Y-axis to align with 2D model
    # (A-ring on the right, D-ring on the left)
    matrix = np.eye(4)
    # Cos(180) = -1, Sin(180) = 0
    matrix[0, 0] = -1
    matrix[2, 2] = -1
    rdMolTransforms.TransformConformer(mol.GetConformer(0), matrix)

    # Render the 3D conformation to a 2D PNG (pseudo-3D)
    d2d = MolDraw2DCairo(400, 400)
    d2d.DrawMolecule(mol)
    d2d.FinishDrawing()
    d2d.WriteDrawingText(output_path)
    return True

async def render_3d_spacefilling(smiles, output_path, x_rot=20, y_rot=20):
    """Generates a 3D spacefilling PNG image from a SMILES string using 3Dmol.js and Playwright."""
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return False

    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    if AllChem.EmbedMolecule(mol, params) == -1:
        return False

    # Get MolBlock
    mol_block = Chem.MolToMolBlock(mol)

    html_content = f"""
    <html>
    <head>
        <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
    </head>
    <body>
        <div id="container" style="width: 400px; height: 400px; position: relative;"></div>
        <script>
            let element = document.getElementById('container');
            let config = {{ backgroundColor: 'white' }};
            let viewer = $3Dmol.createViewer(element, config);
            viewer.addModel(`{mol_block}`, "mol");
            viewer.setStyle({{ sphere: {{}} }});
            viewer.zoomTo();
            viewer.rotate({x_rot}, 'x');
            viewer.rotate({y_rot}, 'y');
            viewer.zoom(0.8);
            viewer.render();
            // Signal that rendering is complete
            window.renderComplete = true;
        </script>
    </body>
    </html>
    """

    temp_html = "temp_mol.html"
    with open(temp_html, "w") as f:
        f.write(html_content)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file://{os.path.abspath(temp_html)}")
        # Wait for the viewer to signal render completion
        await page.wait_for_function("window.renderComplete === true")
        await page.locator("#container").screenshot(path=output_path)
        await browser.close()

    if os.path.exists(temp_html):
        os.remove(temp_html)

    return True

async def render_3d_animation(smiles, output_path, num_frames=20):
    """Generates an animated 3D spacefilling GIF from a SMILES string using 3Dmol.js and Playwright."""
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return False

    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    if AllChem.EmbedMolecule(mol, params) == -1:
        return False

    # Get MolBlock
    mol_block = Chem.MolToMolBlock(mol)

    html_content = f"""
    <html>
    <head>
        <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
    </head>
    <body>
        <div id="container" style="width: 400px; height: 400px; position: relative;"></div>
        <script>
            let element = document.getElementById('container');
            let config = {{ backgroundColor: 'white' }};
            let viewer = $3Dmol.createViewer(element, config);
            viewer.addModel(`{mol_block}`, "mol");
            viewer.setStyle({{ sphere: {{}} }});
            viewer.zoomTo();
            viewer.rotate(20, 'x');
            viewer.zoom(0.8);
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

    temp_html = "temp_anim.html"
    with open(temp_html, "w") as f:
        f.write(html_content)

    frames = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file://{os.path.abspath(temp_html)}")
        await page.wait_for_function("window.renderComplete === true")

        angle_step = 360 / num_frames
        for i in range(num_frames):
            frame_path = f"temp_frame_{i}.png"
            await page.evaluate(f"window.rotateAndRender({angle_step})")
            await page.locator("#container").screenshot(path=frame_path)
            frames.append(Image.open(frame_path))

        await browser.close()

    if frames:
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )
        # Close images to allow deletion
        for img in frames:
            img.close()

    # Cleanup temp files
    for i in range(num_frames):
        frame_path = f"temp_frame_{i}.png"
        if os.path.exists(frame_path):
            os.remove(frame_path)

    if os.path.exists(temp_html):
        os.remove(temp_html)

    return True

async def generate_renders():
    """Reads chemicals from cache and generates renders."""
    cache_path = 'src/cache/chemicals.json'
    if not os.path.exists(cache_path):
        print(f"Cache file not found: {cache_path}")
        return

    with open(cache_path, 'r') as f:
        data = json.load(f)

    output_dir = 'output/images'
    os.makedirs(output_dir, exist_ok=True)

    for name, info in data.items():
        smiles = info['smiles']

        # 2D Rendering
        path_2d = os.path.join(output_dir, f"{name.lower()}_2d.png")
        if render_2d(smiles, path_2d):
            print(f"Generated 2D render for {name} at {path_2d}")
        else:
            print(f"Failed to generate 2D render for {name}")

        # 3D Rendering (Pseudo-3D)
        path_3d = os.path.join(output_dir, f"{name.lower()}_3d.png")
        if render_3d(smiles, path_3d):
            print(f"Generated 3D render for {name} at {path_3d}")
        else:
            print(f"Failed to generate 3D render for {name}")

        # 3D Spacefilling Rendering
        views = [
            ("", 20, 20),
            ("_backside", 20, 200),
            ("_top", 110, 20)
        ]
        for suffix, x_rot, y_rot in views:
            path_sf = os.path.join(output_dir, f"{name.lower()}_spacefilling{suffix}.png")
            if await render_3d_spacefilling(smiles, path_sf, x_rot, y_rot):
                print(f"Generated 3D spacefilling render ({suffix or 'front'}) for {name} at {path_sf}")
            else:
                print(f"Failed to generate 3D spacefilling render ({suffix or 'front'}) for {name}")

        # 3D Animation Rendering
        path_anim = os.path.join(output_dir, f"{name.lower()}_animation.gif")
        if await render_3d_animation(smiles, path_anim):
            print(f"Generated 3D animation for {name} at {path_anim}")
        else:
            print(f"Failed to generate 3D animation for {name}")

if __name__ == "__main__":
    asyncio.run(generate_renders())
