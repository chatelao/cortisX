import os
import asyncio
import urllib.request
from playwright.async_api import async_playwright
from PIL import Image

def download_and_filter_pdb(pdb_id, excluded_chains):
    """Downloads PDB data and filters out specified chains."""
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    try:
        with urllib.request.urlopen(url) as response:
            pdb_data = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error downloading PDB {pdb_id}: {e}")
        return None

    filtered_lines = []
    for line in pdb_data.splitlines():
        if line.startswith(("ATOM", "HETATM")):
            # Chain ID is at column 21 (index 21) in PDB format
            chain_id = line[21].strip()
            if chain_id in excluded_chains:
                continue
        filtered_lines.append(line)

    return "\n".join(filtered_lines)

async def render_enzyme(pdb_id, output_path, excluded_chains=['A', 'B'], style_chains=['C', 'D'], animate_path=None):
    """Generates 3D static and optionally animated images of the enzyme."""

    pdb_content = download_and_filter_pdb(pdb_id, excluded_chains)
    if not pdb_content:
        return False

    # Escape backticks and other characters for JavaScript string
    pdb_content_js = pdb_content.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")

    html_content = f"""
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.4.2/3Dmol-min.js"></script>
    </head>
    <body>
        <div id="container" style="width: 800px; height: 600px; position: relative;"></div>
        <script>
            let element = document.getElementById('container');
            let config = {{ backgroundColor: 'white' }};
            let viewer = $3Dmol.createViewer(element, config);

            let pdbData = `{pdb_content_js}`;
            viewer.addModel(pdbData, "pdb");

            // Style the protein chains
            viewer.setStyle({{chain: {style_chains}}}, {{ cartoon: {{ color: 'lightgray', opacity: 0.7 }} }});

            // Highlight Ligand (NDP - Cofactor) as green sticks and spheres
            viewer.addStyle({{ resn: 'NDP' }}, {{ stick: {{ colorscheme: 'greenCarbon' }}, sphere: {{ colorscheme: 'greenCarbon', scale: 0.3 }} }});

            // Highlight Ligand (BVT - Steroid-like inhibitor) as magenta sticks and spheres
            viewer.addStyle({{ resn: 'BVT' }}, {{ stick: {{ colorscheme: 'magentaCarbon' }}, sphere: {{ colorscheme: 'magentaCarbon', scale: 0.3 }} }});

            // Highlight Catalytic Residues: Ser170, Tyr183, Lys187 as red spheres
            viewer.addStyle({{ resi: [170, 183, 187], resn: ['SER', 'TYR', 'LYS'] }}, {{ sphere: {{ color: 'red', scale: 0.5 }} }});

            viewer.zoomTo();
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

    temp_html = "temp_enzyme.html"
    with open(temp_html, "w") as f:
        f.write(html_content)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 800, "height": 600})
        await page.goto(f"file://{os.path.abspath(temp_html)}")
        await page.wait_for_function("window.renderComplete === true", timeout=60000)

        # Capture static image
        await page.locator("#container").screenshot(path=output_path)
        print(f"Captured static image to {output_path}")

        # Capture animation if path provided
        if animate_path:
            num_frames = 20
            angle_step = 360 / num_frames
            frames = []
            for i in range(num_frames):
                frame_path = f"temp_enzyme_frame_{i}.png"
                await page.evaluate(f"window.rotateAndRender({angle_step})")
                await page.locator("#container").screenshot(path=frame_path)
                frames.append(Image.open(frame_path))

            if frames:
                frames[0].save(
                    animate_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=100,
                    loop=0
                )
                for img in frames:
                    img.close()
                print(f"Captured animation to {animate_path}")

            # Cleanup frames
            for i in range(num_frames):
                frame_path = f"temp_enzyme_frame_{i}.png"
                if os.path.exists(frame_path):
                    os.remove(frame_path)

        await browser.close()

    if os.path.exists(temp_html):
        os.remove(temp_html)

    return True

if __name__ == "__main__":
    output_dir = 'output/images'
    os.makedirs(output_dir, exist_ok=True)
    path_enzyme = os.path.join(output_dir, "enzyme_11bhsd1.png")
    path_enzyme_anim = os.path.join(output_dir, "enzyme_11bhsd1_animation.gif")

    print(f"Rendering enzyme 1XU7 with embedded ligands...")
    asyncio.run(render_enzyme("1XU7", path_enzyme, animate_path=path_enzyme_anim))
    print("Done.")
