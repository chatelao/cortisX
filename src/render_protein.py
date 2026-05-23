import os
import asyncio
import urllib.request
from playwright.async_api import async_playwright
from PIL import Image

def download_and_filter_pdb(pdb_id, excluded_chains=None):
    """Downloads PDB data and filters out specified chains."""
    if excluded_chains is None:
        excluded_chains = []
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    try:
        with urllib.request.urlopen(url) as response:
            pdb_data = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error downloading PDB {pdb_id}: {e}")
        return None

    if not excluded_chains:
        return pdb_data

    filtered_lines = []
    for line in pdb_data.splitlines():
        if line.startswith(("ATOM", "HETATM")):
            # Chain ID is at column 21 (index 21) in PDB format
            chain_id = line[21].strip()
            if chain_id in excluded_chains:
                continue
        filtered_lines.append(line)

    return "\n".join(filtered_lines)

def get_3dmol_style_js():
    """Returns the JavaScript styling code for 3Dmol.js to ensure consistency."""
    return """
        // Professional styling: Light colors and transparency
        let styleHelix = { cartoon: { color: '#FF8C00', opacity: 0.6 } }; // DarkOrange
        let styleSheet = { cartoon: { color: '#87CEFA', opacity: 0.6 } }; // LightSkyBlue
        let styleCoil  = { cartoon: { color: '#DDA0DD', opacity: 0.6 } }; // Plum

        viewer.setStyle({ss: 'h'}, styleHelix);
        viewer.setStyle({ss: 's'}, styleSheet);
        viewer.setStyle({ss: 'c'}, styleCoil);

        // Highlight the cofactor (NDP)
        viewer.addStyle({ resn: 'NDP' },
                       { stick: { colorscheme: 'greenCarbon', radius: 0.25 },
                         sphere: { colorscheme: 'greenCarbon', radius: 0.4, opacity: 0.8 } });

        // Highlight the steroid-like ligand (BVT) to show interaction
        viewer.addStyle({ resn: 'BVT' },
                       { stick: { colorscheme: 'magentaCarbon', radius: 0.3 },
                         sphere: { colorscheme: 'magentaCarbon', radius: 0.5 } });

        // Highlight catalytic triad (Ser170, Tyr183, Lys187)
        viewer.addStyle({ resi: [170, 183, 187] },
                       { stick: { color: '#E74C3C', radius: 0.25 } });

        viewer.zoomTo();
    """

async def render_enzyme(pdb_id, output_path):
    """Generates a high-quality 3D PNG image of the 11b-HSD1 enzyme dimer."""
    pdb_content = download_and_filter_pdb(pdb_id, excluded_chains=['C', 'D'])
    if not pdb_content:
        return False

    pdb_content_js = pdb_content.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    style_js = get_3dmol_style_js()

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

            {style_js}

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

async def render_active_site(pdb_id, output_path):
    """Generates a close-up 3D PNG image of the 11b-HSD1 active site."""
    # Using only Chain A for the close-up to avoid clutter
    pdb_content = download_and_filter_pdb(pdb_id, excluded_chains=['B', 'C', 'D'])
    if not pdb_content:
        return False

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

            // Style the protein as semi-transparent cartoon
            viewer.setStyle({{}}, {{ cartoon: {{ color: 'lightgray', opacity: 0.3 }} }});

            // Highlight the cofactor (NDP)
            viewer.addStyle({{ resn: 'NDP' }},
                           {{ stick: {{ colorscheme: 'greenCarbon', radius: 0.2 }},
                             sphere: {{ colorscheme: 'greenCarbon', radius: 0.4, opacity: 0.6 }} }});
            viewer.addLabel("NADPH (Cofactor)", {{ font: 'sans-serif', fontSize: 18, fontColor: 'darkgreen', backgroundColor: 'white', backgroundOpacity: 0.7 }}, {{ resn: 'NDP' }});

            // Highlight the steroid-like ligand (BVT)
            viewer.addStyle({{ resn: 'BVT' }},
                           {{ stick: {{ colorscheme: 'magentaCarbon', radius: 0.25 }},
                             sphere: {{ colorscheme: 'magentaCarbon', radius: 0.5 }} }});
            viewer.addLabel("Steroid (Substrate Site)", {{ font: 'sans-serif', fontSize: 20, fontColor: 'darkmagenta', backgroundColor: 'white', backgroundOpacity: 0.8 }}, {{ resn: 'BVT' }});

            // Highlight catalytic triad (Ser170, Tyr183, Lys187)
            viewer.addStyle({{ resi: [170, 183, 187] }},
                           {{ stick: {{ color: '#E74C3C', radius: 0.2 }} }});

            viewer.addLabel("Ser170", {{ fontSize: 14, fontColor: '#E74C3C' }}, {{ resi: 170, atom: 'OG' }});
            viewer.addLabel("Tyr183", {{ fontSize: 14, fontColor: '#E74C3C' }}, {{ resi: 183, atom: 'OH' }});
            viewer.addLabel("Lys187", {{ fontSize: 14, fontColor: '#E74C3C' }}, {{ resi: 187, atom: 'NZ' }});

            // Zoom into the ligand
            viewer.zoomTo({{ resn: 'BVT' }});
            viewer.render();
            window.renderComplete = true;
        </script>
    </body>
    </html>
    """

    temp_html = "temp_active_site.html"
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

async def render_enzyme_animation(pdb_id, output_path, num_frames=24):
    """Generates an animated GIF of the rotating 11b-HSD1 enzyme dimer."""
    pdb_content = download_and_filter_pdb(pdb_id, excluded_chains=['C', 'D'])
    if not pdb_content:
        return False

    pdb_content_js = pdb_content.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    style_js = get_3dmol_style_js()

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

            {style_js}

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

    temp_html = "temp_anim_protein.html"
    with open(temp_html, "w") as f:
        f.write(html_content)

    frames = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 800, "height": 600})
        await page.goto(f"file://{os.path.abspath(temp_html)}")
        await page.wait_for_function("window.renderComplete === true")

        angle_step = 360 / num_frames
        for i in range(num_frames):
            frame_path = f"temp_protein_frame_{i}.png"
            await page.evaluate(f"window.rotateAndRender({angle_step})")
            await page.locator("#container").screenshot(path=frame_path)
            frames.append(Image.open(frame_path))

        await browser.close()

    if frames:
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=80,
            loop=0
        )
        for img in frames:
            img.close()

    # Cleanup
    for i in range(num_frames):
        frame_path = f"temp_protein_frame_{i}.png"
        if os.path.exists(frame_path):
            os.remove(frame_path)

    if os.path.exists(temp_html):
        os.remove(temp_html)

    return True

if __name__ == "__main__":
    output_dir = 'output/images'
    os.makedirs(output_dir, exist_ok=True)

    path_enzyme = os.path.join(output_dir, "enzyme_11bhsd1.png")
    path_active = os.path.join(output_dir, "enzyme_11bhsd1_active_site.png")
    path_anim = os.path.join(output_dir, "enzyme_11bhsd1_animation.gif")

    print(f"Rendering refined enzyme visualization (1XU7 dimer with BVT ligand) to {path_enzyme}...")
    asyncio.run(render_enzyme("1XU7", path_enzyme))

    print(f"Rendering active site close-up to {path_active}...")
    asyncio.run(render_active_site("1XU7", path_active))

    print(f"Rendering refined enzyme animation to {path_anim}...")
    asyncio.run(render_enzyme_animation("1XU7", path_anim))

    print("Done.")
