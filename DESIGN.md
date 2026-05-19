# Design - Cortisol vs. Cortisone Comparison

## Technological Choices (Derived from CONCEPT.md)

- **Language**: Python 3.x for scripting, data processing, and interfacing with chemical tools.
- **Data Acquisition**: `rdkit` and `PubChemPy` for retrieving and manipulating chemical data.
- **3D Rendering**: `Py3Dmol` or `NGLView` for generating interactive and static 3D molecular renders.
- **Documentation**: Markdown and LaTeX as the primary formats, with `mkdocs` for generating a static site.
- **CI/CD**: GitHub Actions for automated testing, rendering, and LaTeX validation.

## Detailed Architecture

![Top Architecture](./TOP_ARCHITECTURE.puml)
*(Note: This diagram is dynamically rendered from the PlantUML source)*

The system follows a modular pipeline:
1. **Source Handler**: Interfaces with PubChem API to fetch SMILES and properties.
2. **Chem Processor**: Uses RDKit to calculate descriptors and prepare data for rendering.
3. **Renderer**: Generates PNG/SVG files for 2D formulas and 3D scenes.
4. **Assembler**: Injects data and image links into `REPORT.md` and LaTeX templates.

## Technical Implementation Choice: Rendering Engine

Three alternatives were considered for molecular rendering:

1. **RDKit Draw**:
   - *Pros*: Built-in, extremely fast, excellent 2D support.
   - *Cons*: Limited 3D capabilities.
2. **PyMOL**:
   - *Pros*: Industry standard for high-quality 3D renders.
   - *Cons*: Heavy dependency, potentially difficult to set up in headless CI environments.
3. **Py3Dmol [CHOSEN]**:
   - *Pros*: Lightweight, WebGL-based, easy to integrate into web/markdown environments, handles 3D well.
   - *Cons*: Requires JavaScript for interactivity, but can export static images.

### Discarded Alternatives Summary
- **RDKit Draw**: Discarded for 3D rendering as it is primarily a 2D tool.
- **PyMOL**: Discarded due to complex setup and heavy resource requirements for a minimal project.

## Database
No traditional SQL database is required. Local caching will be implemented using JSON files in `src/cache/`.
- Entity: `ChemicalData`
  - `name`: String
  - `smiles`: String
  - `properties`: JSON
  - `last_updated`: Timestamp
