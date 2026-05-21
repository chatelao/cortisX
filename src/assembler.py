import json
import os
import re

class Assembler:
    """Assembles the final report in Markdown and LaTeX formats."""

    def __init__(self, cache_path='src/cache/chemicals.json', spec_dir='specification/'):
        self.cache_path = cache_path
        self.spec_dir = spec_dir
        self.chemicals = {}
        self.medical_comparison = ""
        self.pregnancy_content = ""
        self.organs_proteins = ""
        self.medications_appendix = ""

    def load_data(self):
        """Loads data from cache and specification files."""
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r') as f:
                self.chemicals = json.load(f)

        med_path = os.path.join(self.spec_dir, 'medical_comparison.md')
        if os.path.exists(med_path):
            with open(med_path, 'r') as f:
                self.medical_comparison = f.read()

        organs_path = os.path.join(self.spec_dir, 'organs_proteins.md')
        if os.path.exists(organs_path):
            with open(organs_path, 'r') as f:
                self.organs_proteins = f.read()

        appendix_path = os.path.join(self.spec_dir, 'medications_appendix.md')
        if os.path.exists(appendix_path):
            with open(appendix_path, 'r') as f:
                self.medications_appendix = f.read()

        pregnancy_path = os.path.join(self.spec_dir, 'pregnancy.md')
        if os.path.exists(pregnancy_path):
            with open(pregnancy_path, 'r') as f:
                self.pregnancy_content = f.read()

        if not self.chemicals or not self.medical_comparison or not self.pregnancy_content or not self.organs_proteins or not self.medications_appendix:
            print("Warning: Some source data is missing.")
            return False
        return True

    def generate_markdown_table(self):
        """Generates a Markdown comparison table for the chemicals."""
        if not self.chemicals:
            return "No chemical data available."

        headers = ["Property"] + list(self.chemicals.keys())
        table = "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        properties = [
            ("PubChem CID", "cid"),
            ("Molecular Formula", "molecular_formula"),
            ("Molecular Weight (g/mol)", "molecular_weight"),
            ("SMILES", "smiles")
        ]

        for label, key in properties:
            row = [label]
            for chem in self.chemicals.values():
                row.append(str(chem.get(key, "N/A")))
            table += "| " + " | ".join(row) + " |\n"
        return table

    def escape_latex(self, text):
        """Escapes LaTeX special characters."""
        # Map of special characters to their escaped versions
        mapping = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '\\': r'\textbackslash{}',
            'β': r'\texorpdfstring{$\beta$}{beta}',
            'α': r'\texorpdfstring{$\alpha$}{alpha}',
            'κ': r'\texorpdfstring{$\kappa$}{kappa}',
            '≈': r'$\approx$'
        }
        # Regex to find these characters
        # Sort keys by length descending to ensure longer sequences are matched first
        regex_pattern = '|'.join(re.escape(str(key)) for key in sorted(mapping.keys(), key=len, reverse=True))
        regex = re.compile(regex_pattern)
        return regex.sub(lambda match: mapping[match.group()], text)

    def md_to_tex(self, md_text):
        """Simple Markdown to LaTeX converter."""
        # First, handle tables separately to avoid escaping their internal structure incorrectly
        lines = md_text.split('\n')
        new_lines = []
        in_table = False

        for line in lines:
            stripped = line.strip()

            # Horizontal rule
            if stripped == '---':
                if in_table:
                    in_table = False
                    new_lines.append('\\end{tabular}')
                    new_lines.append('\\end{center}')
                new_lines.append('\\hrulefill')
                continue

            if stripped.startswith('|') and stripped.endswith('|'):
                if not in_table:
                    in_table = True
                    cols = stripped.count('|') - 1
                    new_lines.append('\\begin{center}')
                    new_lines.append('\\begin{tabularx}{\\textwidth}{|' + 'X|' * cols + '}')
                    new_lines.append('\\hline')
                    content = stripped.strip('|').split('|')
                    content = [self.escape_latex(c.strip()) for c in content]
                    new_lines.append(' & '.join(content) + ' \\\\')
                    new_lines.append('\\hline')
                elif '---' in line:
                    continue
                else:
                    content = stripped.strip('|').split('|')
                    content = [self.escape_latex(c.strip()) for c in content]
                    new_lines.append(' & '.join(content) + ' \\\\')
                    new_lines.append('\\hline')
            else:
                if in_table:
                    in_table = False
                    new_lines.append('\\end{tabularx}')
                    new_lines.append('\\end{center}')

                # Apply LaTeX formatting FIRST for headers to preserve their structure
                processed_line = line
                is_header = False
                if processed_line.startswith('### '):
                    processed_line = f'\\subsubsection{{{self.escape_latex(processed_line[4:])}}}'
                    is_header = True
                elif processed_line.startswith('## '):
                    processed_line = f'\\subsection{{{self.escape_latex(processed_line[3:])}}}'
                    is_header = True
                elif processed_line.startswith('# '):
                    processed_line = f'\\section{{{self.escape_latex(processed_line[2:])}}}'
                    is_header = True

                if not is_header:
                    # Special handling for images BEFORE general escaping
                    image_match = re.search(r'!\[(.*?)\]\((.*?)\)', processed_line)
                    if image_match:
                        alt_text = self.escape_latex(image_match.group(1))
                        image_path = image_match.group(2)
                        processed_line = f"\\begin{{figure}}[h]\n\\centering\n\\includegraphics[width=0.6\\textwidth]{{{image_path}}}\n\\caption{{{alt_text}}}\n\\end{{figure}}"
                    else:
                        # Apply LaTeX escaping and then Markdown formatting for regular lines
                        processed_line = self.escape_latex(processed_line)
                        # Bold
                        processed_line = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', processed_line)
                        # Italic
                        processed_line = re.sub(r'\*(.*?)\*', r'\\textit{\1}', processed_line)

                new_lines.append(processed_line)

        if in_table:
            new_lines.append('\\end{tabularx}')
            new_lines.append('\\end{center}')

        return '\n'.join(new_lines)

    def assemble(self, md_template_path='src/templates/report_template.md',
                 tex_template_path='src/templates/report_template.tex',
                 output_md='REPORT.md', output_tex='report.tex'):
        """Populates templates and writes the final reports."""
        if not self.load_data():
            print("Aborting assembly due to missing data.")
            return

        # Generate Markdown Report
        if os.path.exists(md_template_path):
            with open(md_template_path, 'r') as f:
                md_template = f.read()

            md_report = md_template.replace('{{COMPARISON_TABLE}}', self.generate_markdown_table())
            md_report = md_report.replace('{{MEDICAL_CONTENT}}', self.medical_comparison)
            md_report = md_report.replace('{{PREGNANCY_CONTENT}}', self.pregnancy_content)
            md_report = md_report.replace('{{ORGANS_CONTENT}}', self.organs_proteins)
            md_report = md_report.replace('{{APPENDIX_CONTENT}}', self.medications_appendix)

            # Add chemical descriptions
            for name, data in self.chemicals.items():
                placeholder = "{{" + name.upper() + "_DESCRIPTION}}"
                description = data.get('description', 'No description available.')
                md_report = md_report.replace(placeholder, description)

            with open(output_md, 'w') as f:
                f.write(md_report)
            print(f"Generated {output_md}")

        # Generate LaTeX Report
        if os.path.exists(tex_template_path):
            with open(tex_template_path, 'r') as f:
                tex_template = f.read()

            # Dynamic LaTeX table for chemical properties
            num_chems = len(self.chemicals)
            tex_table = "\\begin{center}\n\\begin{tabularx}{\\textwidth}{|l|" + "X|" * num_chems + "}\n\\hline\n"
            headers = ["Property"] + [self.escape_latex(name) for name in self.chemicals.keys()]
            tex_table += " & ".join(headers) + " \\\\\n\\hline\n"

            properties = [
                ("PubChem CID", "cid"),
                ("Molecular Formula", "molecular_formula"),
                ("Molecular Weight", "molecular_weight")
            ]
            for label, key in properties:
                row = [self.escape_latex(label)]
                for chem in self.chemicals.values():
                    row.append(self.escape_latex(str(chem.get(key, "N/A"))))
                tex_table += " & ".join(row) + " \\\\\n\\hline\n"
            tex_table += "\\end{tabularx}\n\\end{center}"

            tex_report = tex_template.replace('{{COMPARISON_TABLE}}', tex_table)
            tex_report = tex_report.replace('{{MEDICAL_CONTENT}}', self.md_to_tex(self.medical_comparison))
            tex_report = tex_report.replace('{{PREGNANCY_CONTENT}}', self.md_to_tex(self.pregnancy_content))
            tex_report = tex_report.replace('{{ORGANS_CONTENT}}', self.md_to_tex(self.organs_proteins))
            tex_report = tex_report.replace('{{APPENDIX_CONTENT}}', self.md_to_tex(self.medications_appendix))

            # Add chemical descriptions
            for name, data in self.chemicals.items():
                placeholder = "{{" + name.upper() + "_DESCRIPTION}}"
                description = data.get('description', 'No description available.')
                tex_report = tex_report.replace(placeholder, self.escape_latex(description))

            with open(output_tex, 'w') as f:
                f.write(tex_report)
            print(f"Generated {output_tex}")

if __name__ == "__main__":
    assembler = Assembler()
    assembler.assemble()
