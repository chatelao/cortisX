import json
import os
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import MolDraw2DCairo

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

    # Render the 3D conformation to a 2D PNG (pseudo-3D)
    d2d = MolDraw2DCairo(400, 400)
    d2d.DrawMolecule(mol)
    d2d.FinishDrawing()
    d2d.WriteDrawingText(output_path)
    return True

def generate_renders():
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

if __name__ == "__main__":
    generate_renders()
