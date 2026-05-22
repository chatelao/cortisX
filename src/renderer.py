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
from PIL import Image, ImageDraw, ImageFont

def render_2d(smiles, output_path, highlight_atoms=None, highlight_color=(0, 1, 0), rotate_180=False):
    """Generates a 2D PNG image from a SMILES string with optional highlighting and rotation."""
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return False

    # Generate 2D coordinates
    AllChem.Compute2DCoords(mol)

    if rotate_180:
        # Rotate 180 degrees around Z-axis (2D rotation)
        matrix = np.eye(4)
        matrix[0, 0] = -1
        matrix[1, 1] = -1
        rdMolTransforms.TransformConformer(mol.GetConformer(0), matrix)

    d2d = MolDraw2DCairo(400, 400)
    if highlight_atoms:
        # highlightAtomColors expects a dictionary of index: color_tuple
        # RDKit colors are 0-1 for RGB
        d2d.DrawMolecule(mol, highlightAtoms=highlight_atoms,
                        highlightAtomColors={i: highlight_color for i in highlight_atoms})
    else:
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

def render_balance(output_path):
    """Generates a composite 'chemical balance' image of Cortisone <=> Cortisol."""
    cache_path = 'src/cache/chemicals.json'
    if not os.path.exists(cache_path):
        return False

    with open(cache_path, 'r') as f:
        data = json.load(f)

    cortisol_smiles = data.get("Cortisol", {}).get("smiles")
    cortisone_smiles = data.get("Cortisone", {}).get("smiles")

    if not cortisol_smiles or not cortisone_smiles:
        return False

    # Identify differentiating atoms at C11 position
    # Cortisol: hydroxyl at C11. Cortisone: ketone at C11.
    # We use SMARTS to find these specific environments.
    # C11 is a ring carbon (R2) connected to a bridgehead and another ring carbon.
    # SMARTS for Cortisol C11-OH: [C;R2]([OH])
    # SMARTS for Cortisone C11=O: [C;R2](=O)

    mol_cortisol = Chem.MolFromSmiles(cortisol_smiles)
    mol_cortisone = Chem.MolFromSmiles(cortisone_smiles)

    # We target the C-ring C11. C3=O is in A-ring (conjugated).
    # C17-OH has a sidechain.
    # C11 is not conjugated and has no sidechain.
    smarts_cortisol = "[CH;R]([OH])"
    smarts_cortisone = "[C;R](=O)"

    match_cortisol = mol_cortisol.GetSubstructMatches(Chem.MolFromSmarts(smarts_cortisol))
    match_cortisone = mol_cortisone.GetSubstructMatches(Chem.MolFromSmarts(smarts_cortisone))

    # Filtering matches to ensure we get C11
    # For Cortisol, we might get C11 and C17 if we are not careful.
    # But C17 is [C;R1] (if D-ring is considered R1 and C-ring R2? No).
    # Actually, let's use a more specific pattern that includes the bridgehead C9.
    specific_cortisol = "[C;R2]1[C;R2][C;R2]2[C@H](O)C[C;R2]3..." # Too complex.

    # Let's just find all matches and pick the one that isn't C17 or C3.
    # C3 is conjugated. C17 has a side chain C(=O)CO.
    highlight_cortisol = []
    for match in match_cortisol:
        c_idx = match[0]
        # Check if it has a sidechain (C17 has 4 neighbors: C13, C16, O17, C20)
        if len(mol_cortisol.GetAtomWithIdx(c_idx).GetNeighbors()) == 3: # C11 has 3 non-H neighbors: C9, C12, O11
             highlight_cortisol.extend(match)
             break

    highlight_cortisone = []
    for match in match_cortisone:
        c_idx = match[0]
        # C3 is connected to a double bond in the ring.
        atom = mol_cortisone.GetAtomWithIdx(c_idx)
        is_conjugated = False
        for bond in atom.GetBonds():
            if bond.GetIsConjugated():
                is_conjugated = True
        if not is_conjugated:
            highlight_cortisone.extend(match)
            break

    # Render individual 2D images with highlights and 180-degree rotation
    temp_cortisol = "temp_cortisol_2d.png"
    temp_cortisone = "temp_cortisone_2d.png"
    render_2d(cortisol_smiles, temp_cortisol, highlight_atoms=highlight_cortisol, rotate_180=True)
    render_2d(cortisone_smiles, temp_cortisone, highlight_atoms=highlight_cortisone, rotate_180=True)

    img_cortisol = Image.open(temp_cortisol)
    img_cortisone = Image.open(temp_cortisone)

    # Create canvas - increased width to avoid overlap
    canvas_width = 1200
    canvas_height = 400
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    draw = ImageDraw.Draw(canvas)

    # Positions
    y_offset = 50
    canvas.paste(img_cortisone, (100, y_offset))
    canvas.paste(img_cortisol, (700, y_offset))

    # Try to load a font that supports Greek characters
    font_paths = [
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"
    ]
    font = None
    for path in font_paths:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, 24)
                label_font = ImageFont.truetype(path, 28)
                break
            except:
                continue

    if not font:
        font = ImageFont.load_default()
        label_font = ImageFont.load_default()

    # Draw labels
    draw.text((300, 350), "Cortisone", fill="black", font=label_font, anchor="mm")
    draw.text((900, 350), "Cortisol", fill="black", font=label_font, anchor="mm")

    # Draw arrows - adjusted for new canvas width and molecule positions
    arrow_y_top = 180
    arrow_y_bottom = 220
    arrow_x_start = 520
    arrow_x_end = 680

    # Top arrow (Right)
    draw.line([(arrow_x_start, arrow_y_top), (arrow_x_end, arrow_y_top)], fill="black", width=3)
    draw.polygon([(arrow_x_end, arrow_y_top), (arrow_x_end-10, arrow_y_top-5), (arrow_x_end-10, arrow_y_top+5)], fill="black")
    draw.text(((arrow_x_start + arrow_x_end)//2, arrow_y_top - 30), "11β-HSD1", fill="black", font=font, anchor="mm")

    # Bottom arrow (Left)
    draw.line([(arrow_x_start, arrow_y_bottom), (arrow_x_end, arrow_y_bottom)], fill="black", width=3)
    draw.polygon([(arrow_x_start, arrow_y_bottom), (arrow_x_start+10, arrow_y_bottom-5), (arrow_x_start+10, arrow_y_bottom+5)], fill="black")
    draw.text(((arrow_x_start + arrow_x_end)//2, arrow_y_bottom + 30), "11β-HSD2", fill="black", font=font, anchor="mm")

    canvas.save(output_path)

    # Cleanup
    img_cortisol.close()
    img_cortisone.close()
    os.remove(temp_cortisol)
    os.remove(temp_cortisone)

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

    # Chemical Balance Rendering
    path_balance = os.path.join(output_dir, "chemical_balance.png")
    if render_balance(path_balance):
        print(f"Generated chemical balance render at {path_balance}")
    else:
        print("Failed to generate chemical balance render")

    for name, info in data.items():
        smiles = info['smiles']

        # 2D Rendering
        path_2d = os.path.join(output_dir, f"{name.lower()}_2d.png")
        if render_2d(smiles, path_2d):
            print(f"Generated 2D render for {name} at {path_2d}")
        else:
            print(f"Failed to generate 2D render for {name}")

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
