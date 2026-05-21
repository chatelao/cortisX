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
            "smiles": "O",
            "description": "English desc",
            "description_de": "Deutsche Beschreibung"
        }
    }
    with open(cache_file, "w") as f:
        json.dump(chemicals_data, f)

    spec_dir = tmp_path / "specification"
    spec_dir.mkdir()
    # English
    with open(spec_dir / "medical_comparison.md", "w") as f:
        f.write("# Medical\nSome medical info.")
    with open(spec_dir / "organs_proteins.md", "w") as f:
        f.write("# Organs\nSome organ info.")
    with open(spec_dir / "medications_appendix.md", "w") as f:
        f.write("# Appendix\nSome appendix info.")
    with open(spec_dir / "pregnancy.md", "w") as f:
        f.write("# Pregnancy\nSome pregnancy info.")

    # German
    with open(spec_dir / "medical_comparison_de.md", "w") as f:
        f.write("# Medizin\nMedizinische Info.")
    with open(spec_dir / "organs_proteins_de.md", "w") as f:
        f.write("# Organe\nOrgan Info.")
    with open(spec_dir / "medications_appendix_de.md", "w") as f:
        f.write("# Anhang\nAnhang Info.")
    with open(spec_dir / "pregnancy_de.md", "w") as f:
        f.write("# Schwangerschaft\nSchwangerschaft Info.")

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    with open(templates_dir / "report_template.md", "w") as f:
        f.write("{{COMPARISON_TABLE}}\n{{MEDICAL_CONTENT}}\n{{TESTCHEM_DESCRIPTION}}")
    with open(templates_dir / "report_template_de.md", "w") as f:
        f.write("{{COMPARISON_TABLE}}\n{{MEDICAL_CONTENT}}\n{{TESTCHEM_DESCRIPTION}}")
    with open(templates_dir / "report_template.tex", "w") as f:
        f.write("{{COMPARISON_TABLE}}\n{{MEDICAL_CONTENT}}\n{{TESTCHEM_DESCRIPTION}}")
    with open(templates_dir / "report_template_de.tex", "w") as f:
        f.write("{{COMPARISON_TABLE}}\n{{MEDICAL_CONTENT}}\n{{TESTCHEM_DESCRIPTION}}")

    return Assembler(cache_path=str(cache_file), spec_dir=str(spec_dir)), templates_dir, tmp_path

def test_load_data_en(assembler):
    a, _, _ = assembler
    assert a.load_data(lang='en') is True
    assert "TestChem" in a.chemicals
    assert "# Medical" in a.medical_comparison

def test_load_data_de(assembler):
    a, _, _ = assembler
    assert a.load_data(lang='de') is True
    assert "# Medizin" in a.medical_comparison
    assert "# Schwangerschaft" in a.pregnancy_content

def test_generate_markdown_table_en(assembler):
    a, _, _ = assembler
    a.load_data(lang='en')
    table = a.generate_markdown_table(lang='en')
    assert "| Property | TestChem |" in table
    assert "| PubChem CID | 123 |" in table

def test_generate_markdown_table_de(assembler):
    a, _, _ = assembler
    a.load_data(lang='de')
    table = a.generate_markdown_table(lang='de')
    assert "| Eigenschaft | TestChem |" in table
    assert "| Summenformel | H2O |" in table

def test_assemble_de(assembler):
    a, templates_dir, output_dir = assembler
    output_md = output_dir / "BERICHT.md"
    output_tex = output_dir / "bericht.tex"

    a.assemble(
        lang='de',
        md_template_path=str(templates_dir / "report_template_de.md"),
        tex_template_path=str(templates_dir / "report_template_de.tex"),
        output_md=str(output_md),
        output_tex=str(output_tex)
    )

    assert os.path.exists(output_md)
    assert os.path.exists(output_tex)

    with open(output_md, 'r') as f:
        content = f.read()
        assert "Eigenschaft" in content
        assert "Medizinische Info" in content
        assert "Deutsche Beschreibung" in content

    with open(output_tex, 'r') as f:
        content = f.read()
        assert "Eigenschaft" in content
        assert "Deutsche Beschreibung" in content
