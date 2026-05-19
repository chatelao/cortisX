import os
import json
from src.renderer import render_2d, render_3d

def test_render_2d():
    output = "test_2d.png"
    if os.path.exists(output):
        os.remove(output)
    smiles = "C1CCCCC1"
    assert render_2d(smiles, output) is True
    assert os.path.exists(output)
    os.remove(output)

def test_render_3d():
    output = "test_3d.png"
    if os.path.exists(output):
        os.remove(output)
    smiles = "C1CCCCC1"
    assert render_3d(smiles, output) is True
    assert os.path.exists(output)
    os.remove(output)

def test_chemicals_rendering():
    # Test with real data from cache
    with open('src/cache/chemicals.json', 'r') as f:
        data = json.load(f)

    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)

    for name, info in data.items():
        smiles = info['smiles']
        path_2d = os.path.join(output_dir, f"{name}_2d.png")
        path_3d = os.path.join(output_dir, f"{name}_3d.png")

        assert render_2d(smiles, path_2d) is True
        assert os.path.exists(path_2d)

        assert render_3d(smiles, path_3d) is True
        assert os.path.exists(path_3d)

        os.remove(path_2d)
        os.remove(path_3d)

    os.rmdir(output_dir)
