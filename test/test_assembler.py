import os
import json
import pytest
from src.assembler import Assembler

@pytest.fixture
def assembler(tmp_path):
    # Setup mock data and directories
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    cache_file = cache_dir / "chemicals.json"
    chemicals_data = {
        "TestChem": {
            "cid": 123,
            "molecular_formula": "H2O",
            "molecular_weight": 18.0,
            "smiles": "O"
        },
        "Chem_With_Special_Chars": {
            "cid": 456,
            "molecular_formula": "C6H12O6",
            "molecular_weight": 180.1,
            "smiles": "C(C1C(C(C(C(O1)O)O)O)O)O"
        }
    }
    with open(cache_file, "w") as f:
        json.dump(chemicals_data, f)

    spec_dir = tmp_path / "specification"
    spec_dir.mkdir()
    with open(spec_dir / "medical_comparison.md", "w") as f:
        f.write("# Medical\nSome medical info with β and _underscore_.\n---\nNew section.")
    with open(spec_dir / "organs_proteins.md", "w") as f:
        f.write("# Organs\nSome organ info.")

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    with open(templates_dir / "report_template.md", "w") as f:
        f.write("{{COMPARISON_TABLE}}\n{{MEDICAL_CONTENT}}\n{{ORGANS_CONTENT}}")
    with open(templates_dir / "report_template.tex", "w") as f:
        f.write("{{COMPARISON_TABLE}}\n{{MEDICAL_CONTENT}}\n{{ORGANS_CONTENT}}")

    return Assembler(cache_path=str(cache_file), spec_dir=str(spec_dir)), templates_dir, tmp_path

def test_load_data(assembler):
    a, _, _ = assembler
    assert a.load_data() is True
    assert "TestChem" in a.chemicals
    assert "Chem_With_Special_Chars" in a.chemicals
    assert "# Medical" in a.medical_comparison

def test_generate_markdown_table(assembler):
    a, _, _ = assembler
    a.load_data()
    table = a.generate_markdown_table()
    assert "| Property | TestChem | Chem_With_Special_Chars |" in table
    assert "| PubChem CID | 123 | 456 |" in table

def test_escape_latex(assembler):
    a, _, _ = assembler
    text = "beta β, underscore _, ampersand &, dollar $, percent %, hash #"
    escaped = a.escape_latex(text)
    assert r"$\beta$" in escaped
    assert r"\_" in escaped
    assert r"\&" in escaped
    assert r"\$" in escaped
    assert r"\%" in escaped
    assert r"\#" in escaped

def test_md_to_tex(assembler):
    a, _, _ = assembler
    md = "# Title\n## Section\n**Bold**\n---\n| Col1 | Col2 |\n|---|---|\n| Val1 | Val2 |"
    tex = a.md_to_tex(md)
    assert "\\section{Title}" in tex
    assert "\\subsection{Section}" in tex
    assert "\\textbf{Bold}" in tex
    assert "\\hrulefill" in tex
    assert "\\begin{tabular}{|l|l|}" in tex

def test_assemble(assembler):
    a, templates_dir, output_dir = assembler
    output_md = output_dir / "REPORT.md"
    output_tex = output_dir / "report.tex"

    a.assemble(
        md_template_path=str(templates_dir / "report_template.md"),
        tex_template_path=str(templates_dir / "report_template.tex"),
        output_md=str(output_md),
        output_tex=str(output_tex)
    )

    assert os.path.exists(output_md)
    assert os.path.exists(output_tex)

    with open(output_tex, 'r') as f:
        content = f.read()
        assert r"Chem\_With\_Special\_Chars" in content
        assert r"$\beta$" in content
        assert "\\begin{tabular}{|l|l|l|}" in content # Property + 2 chemicals
