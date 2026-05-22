import os
import asyncio
import urllib.request
from playwright.async_api import async_playwright

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

async def render_enzyme(pdb_id, output_path):
    """Generates a 3D PNG image of the filtered enzyme."""

    # Filter out chains A and B (Lower Half)
    pdb_content = download_and_filter_pdb(pdb_id, ['A', 'B'])
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
        <div id="container" style="width: 1200px; height: 900px; position: relative;"></div>
        <script>
            let element = document.getElementById('container');
            let config = {{ backgroundColor: 'white' }};
            let viewer = $3Dmol.createViewer(element, config);

            let pdbData = `{pdb_content_js}`;
            viewer.addModel(pdbData, "pdb");

            // Base style: Loops/Coils as cyan cartoon
            viewer.setStyle({{chain: ['C', 'D']}}, {{ cartoon: {{ color: 'cyan', radius: 0.3 }} }});

            // Alpha Helices: yellow cartoon (semi-transparent)
            viewer.addStyle({{chain: ['C', 'D'], ss: 'h'}}, {{ cartoon: {{ color: 'yellow', opacity: 0.6 }} }});

            // Beta Sheets: yellow cartoon (semi-transparent)
            viewer.addStyle({{chain: ['C', 'D'], ss: 's'}}, {{ cartoon: {{ color: 'yellow', opacity: 0.6, width: 1.2, thickness: 0.6 }} }});

            // Helical sidechains: purple sticks (semi-transparent)
            viewer.addStyle({{chain: ['C', 'D'], ss: 'h'}}, {{ stick: {{ color: 'purple', radius: 0.15, opacity: 0.4 }} }});

            // Sulfur atoms: yellow spheres
            viewer.addStyle({{element: 'S'}}, {{ sphere: {{ color: 'yellow', radius: 0.3 }} }});

            // Ligand (NDP): light green ball-and-stick
            viewer.addStyle({{ resn: 'NDP' }}, {{ stick: {{ color: 'lightgreen', radius: 0.35 }}, sphere: {{ color: 'lightgreen', radius: 0.55 }} }});

            // Catalytic residues (Ser170, Tyr183, Lys187): red sticks
            viewer.addStyle({{ resi: [170, 183, 187], resn: ['SER', 'TYR', 'LYS'] }}, {{ stick: {{ color: 'red', radius: 0.3 }} }});

            viewer.zoomTo();
            viewer.render();
            window.renderComplete = true;
        </script>
    </body>
    </html>
    """

    temp_html = "temp_protein.html"
    with open(temp_html, "w") as f:
        f.write(html_content)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1200, "height": 900})
        await page.goto(f"file://{os.path.abspath(temp_html)}")

        await page.wait_for_function("window.renderComplete === true", timeout=60000)

        await page.locator("#container").screenshot(path=output_path)
        await browser.close()

    if os.path.exists(temp_html):
        os.remove(temp_html)

    return True

if __name__ == "__main__":
    output_dir = 'output/images'
    os.makedirs(output_dir, exist_ok=True)
    path_enzyme = os.path.join(output_dir, "enzyme_11bhsd1.png")

    print(f"Rendering filtered enzyme 1XU7 to {path_enzyme}...")
    asyncio.run(render_enzyme("1XU7", path_enzyme))
    print("Done.")
