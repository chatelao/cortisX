import os
import asyncio
from playwright.async_api import async_playwright

async def render_enzyme(pdb_id, output_path):
    """Generates a 3D spacefilling PNG image of an enzyme with highlighted active site."""

    html_content = f"""
    <html>
    <head>
        <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
    </head>
    <body>
        <div id="container" style="width: 800px; height: 600px; position: relative;"></div>
        <script>
            let element = document.getElementById('container');
            let config = {{ backgroundColor: 'white' }};
            let viewer = $3Dmol.createViewer(element, config);

            $3Dmol.download("pdb:{pdb_id}", viewer, {{}}, function() {{
                // Set global style
                viewer.setStyle({{}}, {{ sphere: {{ color: 'lightgray', opacity: 0.8 }} }});

                // Highlight Ligand (NDP)
                viewer.addStyle({{ resn: 'NDP' }}, {{ sphere: {{ color: 'magenta' }} }});

                // Highlight Catalytic Residues: Ser170, Tyr183, Lys187
                viewer.addStyle({{ resi: [170, 183, 187], resn: ['SER', 'TYR', 'LYS'] }}, {{ sphere: {{ color: 'yellow' }} }});

                viewer.zoomTo();
                viewer.render();
                window.renderComplete = true;
            }});
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
        # Set viewport to match container
        await page.set_viewport_size({"width": 800, "height": 600})
        await page.goto(f"file://{os.path.abspath(temp_html)}")

        # Wait for the viewer to signal render completion
        # We might need a longer timeout for protein download
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

    print(f"Rendering enzyme 1XU7 to {path_enzyme}...")
    asyncio.run(render_enzyme("1XU7", path_enzyme))
    print("Done.")
