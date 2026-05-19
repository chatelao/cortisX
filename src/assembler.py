import json
import os

def load_chemical_data():
    cache_path = 'src/cache/chemicals.json'
    if not os.path.exists(cache_path):
        return {}
    with open(cache_path, 'r') as f:
        return json.load(f)

def load_medical_comparison():
    path = 'specification/medical_comparison.md'
    if not os.path.exists(path):
        return ""
    with open(path, 'r') as f:
        return f.read()

def format_properties_md(data):
    lines = []
    for key, value in data.items():
        if key != 'last_updated':
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"- **{formatted_key}**: {value}")
    return "\n".join(lines)

def format_properties_latex(data):
    lines = ["\\begin{itemize}"]
    for key, value in data.items():
        if key != 'last_updated':
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"  \\item \\textbf{{{formatted_key}}}: {value}")
    lines.append("\\end{itemize}")
    return "\n".join(lines)

def assemble_reports():
    chem_data = load_chemical_data()
    medical_comp = load_medical_comparison()

    # Prepare Markdown replacements
    replacements_md = {
        "{{CORTISOL_PROPERTIES}}": format_properties_md(chem_data.get("Cortisol", {})),
        "{{CORTISONE_PROPERTIES}}": format_properties_md(chem_data.get("Cortisone", {})),
        "{{MEDICAL_COMPARISON}}": medical_comp
    }

    # Prepare LaTeX replacements
    # Basic conversion for medical comparison
    med_comp_latex = medical_comp

    # Handle Tables (very basic conversion for pipe tables)
    lines = med_comp_latex.split('\n')
    new_lines = []
    in_table = False
    for line in lines:
        if line.strip().startswith('|') and '|' in line:
            if not in_table:
                new_lines.append('\\begin{center}')
                # Determine number of columns
                cols = line.count('|') - 1
                new_lines.append('\\begin{tabular}{' + 'l' * cols + '}')
                new_lines.append('\\hline')
                in_table = True

            # Skip separator line
            if '---' in line:
                continue

            # Format table row
            row = line.strip().strip('|').replace('|', ' & ')
            new_lines.append(row + ' \\\\ \\hline')
        else:
            if in_table:
                new_lines.append('\\end{tabular}')
                new_lines.append('\\end{center}')
                in_table = False
            new_lines.append(line)
    if in_table:
        new_lines.append('\\end{tabular}')
        new_lines.append('\\end{center}')

    med_comp_latex = '\n'.join(new_lines)

    med_comp_latex = med_comp_latex.replace('### ', '\\subsubsection{')
    med_comp_latex = med_comp_latex.replace('## ', '\\subsection{')
    med_comp_latex = med_comp_latex.replace('# ', '\\section{')
    # Close the braces for sections
    lines = []
    for line in med_comp_latex.split('\n'):
        if line.startswith('\\section{') or line.startswith('\\subsection{') or line.startswith('\\subsubsection{'):
            lines.append(line + '}')
        else:
            lines.append(line)
    med_comp_latex = '\n'.join(lines)

    # Replace bold
    import re
    med_comp_latex = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', med_comp_latex)
    # Handle itemized lists
    med_comp_latex = re.sub(r'^- (.*)', r'\\begin{itemize}\n  \\item \1\n\\end{itemize}', med_comp_latex, flags=re.MULTILINE)
    # Clean up double itemize
    med_comp_latex = med_comp_latex.replace('\\end{itemize}\n\\begin{itemize}', '')

    replacements_latex = {
        "{{CORTISOL_PROPERTIES_LATEX}}": format_properties_latex(chem_data.get("Cortisol", {})),
        "{{CORTISONE_PROPERTIES_LATEX}}": format_properties_latex(chem_data.get("Cortisone", {})),
        "{{MEDICAL_COMPARISON_LATEX}}": med_comp_latex
    }

    # Generate REPORT.md
    with open('src/templates/report_template.md', 'r') as f:
        content_md = f.read()
    for placeholder, value in replacements_md.items():
        content_md = content_md.replace(placeholder, value)

    with open('REPORT.md', 'w') as f:
        f.write(content_md)
    print("Generated REPORT.md")

    # Generate report.tex
    with open('src/templates/report_template.tex', 'r') as f:
        content_latex = f.read()
    for placeholder, value in replacements_latex.items():
        content_latex = content_latex.replace(placeholder, value)

    with open('report.tex', 'w') as f:
        f.write(content_latex)
    print("Generated report.tex")

if __name__ == "__main__":
    assemble_reports()
