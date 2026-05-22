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

    def load_data(self, lang='en'):
        """Loads data from cache and specification files."""
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r') as f:
                self.chemicals = json.load(f)

        suffix = f"_{lang}" if lang != 'en' else ""

        med_path = os.path.join(self.spec_dir, f'medical_comparison{suffix}.md')
        if os.path.exists(med_path):
            with open(med_path, 'r') as f:
                self.medical_comparison = f.read()

        organs_path = os.path.join(self.spec_dir, f'organs_proteins{suffix}.md')
        if os.path.exists(organs_path):
            with open(organs_path, 'r') as f:
                self.organs_proteins = f.read()

        appendix_path = os.path.join(self.spec_dir, f'medications_appendix{suffix}.md')
        if os.path.exists(appendix_path):
            with open(appendix_path, 'r') as f:
                self.medications_appendix = f.read()

        pregnancy_path = os.path.join(self.spec_dir, f'pregnancy{suffix}.md')
        if os.path.exists(pregnancy_path):
            with open(pregnancy_path, 'r') as f:
                self.pregnancy_content = f.read()

        if not self.chemicals or not self.medical_comparison or not self.pregnancy_content or not self.organs_proteins or not self.medications_appendix:
            print(f"Warning: Some source data is missing for language '{lang}'.")
            return False
        return True

    def format_formula(self, formula, mode='md'):
        """Formats a chemical formula with subscripts."""
        if mode == 'md':
            return re.sub(r'(\d+)', r'<sub>\1</sub>', formula)
        elif mode == 'tex':
            # Escape the formula first, then add textsubscript
            # but wait, molecular formula doesn't usually have special latex chars
            # except maybe if we already escaped it.
            return re.sub(r'(\d+)', r'\\textsubscript{\1}', formula)
        return formula

    def generate_markdown_table(self, lang='en'):
        """Generates a Markdown comparison table for the chemicals."""
        if not self.chemicals:
            return "No chemical data available."

        prop_label = "Property" if lang == 'en' else "Eigenschaft"
        headers = [prop_label] + list(self.chemicals.keys())
        table = "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        properties_en = [
            ("PubChem CID", "cid"),
            ("Molecular Formula", "molecular_formula"),
            ("Molecular Weight (g/mol)", "molecular_weight"),
            ("SMILES", "smiles")
        ]
        properties_de = [
            ("PubChem CID", "cid"),
            ("Summenformel", "molecular_formula"),
            ("Molekulargewicht (g/mol)", "molecular_weight"),
            ("SMILES", "smiles")
        ]
        properties = properties_en if lang == 'en' else properties_de

        for label, key in properties:
            row = [label]
            for chem in self.chemicals.values():
                val = str(chem.get(key, "N/A"))
                if key == "molecular_formula":
                    val = self.format_formula(val, mode='md')
                row.append(val)
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
                    # HTML subscripts to LaTeX
                    content = [re.sub(r'<sub>(.*?)</sub>', r'\\textsubscript{\1}', c) for c in content]
                    new_lines.append(' & '.join(content) + ' \\\\')
                    new_lines.append('\\hline')
                elif '---' in line:
                    continue
                else:
                    content = stripped.strip('|').split('|')
                    content = [self.escape_latex(c.strip()) for c in content]
                    # HTML subscripts to LaTeX
                    content = [re.sub(r'<sub>(.*?)</sub>', r'\\textsubscript{\1}', c) for c in content]
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
                if processed_line.startswith('#### '):
                    processed_line = f'\\subsubsection*{{{self.escape_latex(processed_line[5:])}}}'
                    is_header = True
                elif processed_line.startswith('### '):
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
                        # Extract links to avoid escaping them
                        links = []
                        def placeholder(match):
                            links.append(match.groups())
                            return f"LINKPLACEHOLDER{len(links)-1}"

                        processed_line = re.sub(r'\[(.*?)\]\((.*?)\)', placeholder, processed_line)

                        # Apply LaTeX escaping for the rest of the text
                        processed_line = self.escape_latex(processed_line)

                        # Restore links with proper LaTeX format
                        for i, (text, url) in enumerate(links):
                            # The URL should NOT be escaped by our simple escape_latex as it's used in \href
                            # But hyphens are fine. Underscores in URLs might need care.
                            # \href handles underscores if you use the right packages or escape them.
                            # Since we already escaped the rest of the line, and URLs here are protein atlas URLs
                            # which mostly use hyphens, it should be fine.
                            # We should escape underscores in URL for \href just in case.
                            url_tex = url.replace('_', r'\_').replace('%', r'\%').replace('#', r'\#')
                            text_tex = self.escape_latex(text)
                            # HTML subscripts in link text
                            text_tex = re.sub(r'<sub>(.*?)</sub>', r'\\textsubscript{\1}', text_tex)
                            processed_line = processed_line.replace(f"LINKPLACEHOLDER{i}", f"\\href{{{url_tex}}}{{{text_tex}}}")

                        # HTML subscripts to LaTeX
                        processed_line = re.sub(r'<sub>(.*?)</sub>', r'\\textsubscript{\1}', processed_line)
                        # Bold
                        processed_line = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', processed_line)
                        # Italic
                        processed_line = re.sub(r'\*(.*?)\*', r'\\textit{\1}', processed_line)

                new_lines.append(processed_line)

        if in_table:
            new_lines.append('\\end{tabularx}')
            new_lines.append('\\end{center}')

        return '\n'.join(new_lines)

    def assemble(self, lang='en',
                 md_template_path=None,
                 tex_template_path=None,
                 output_md=None, output_tex=None):
        """Populates templates and writes the final reports."""
        if not self.load_data(lang=lang):
            print(f"Aborting assembly for '{lang}' due to missing data.")
            return

        suffix = f"_{lang}" if lang != 'en' else ""
        if md_template_path is None:
            md_template_path = f'src/templates/report_template{suffix}.md'
        if tex_template_path is None:
            tex_template_path = f'src/templates/report_template{suffix}.tex'
        if output_md is None:
            output_md = 'REPORT.md' if lang == 'en' else 'BERICHT.md'
        if output_tex is None:
            output_tex = 'report.tex' if lang == 'en' else 'bericht.tex'

        # Generate Markdown Report
        if os.path.exists(md_template_path):
            with open(md_template_path, 'r') as f:
                md_template = f.read()

            md_report = md_template.replace('{{COMPARISON_TABLE}}', self.generate_markdown_table(lang=lang))
            md_report = md_report.replace('{{MEDICAL_CONTENT}}', self.medical_comparison)
            md_report = md_report.replace('{{PREGNANCY_CONTENT}}', self.pregnancy_content)
            md_report = md_report.replace('{{ORGANS_CONTENT}}', self.organs_proteins)
            md_report = md_report.replace('{{APPENDIX_CONTENT}}', self.medications_appendix)

            # Add chemical descriptions
            desc_key = 'description' if lang == 'en' else f'description_{lang}'
            for name, data in self.chemicals.items():
                placeholder = "{{" + name.upper() + "_DESCRIPTION}}"
                description = data.get(desc_key, data.get('description', 'No description available.'))
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
            prop_label = "Property" if lang == 'en' else "Eigenschaft"
            headers = [prop_label] + [self.escape_latex(name) for name in self.chemicals.keys()]
            tex_table += " & ".join(headers) + " \\\\\n\\hline\n"

            properties_en = [
                ("PubChem CID", "cid"),
                ("Molecular Formula", "molecular_formula"),
                ("Molecular Weight", "molecular_weight")
            ]
            properties_de = [
                ("PubChem CID", "cid"),
                ("Summenformel", "molecular_formula"),
                ("Molekulargewicht", "molecular_weight")
            ]
            properties = properties_en if lang == 'en' else properties_de

            for label, key in properties:
                row = [self.escape_latex(label)]
                for chem in self.chemicals.values():
                    val = str(chem.get(key, "N/A"))
                    if key == "molecular_formula":
                        val = self.format_formula(val, mode='tex')
                    else:
                        val = self.escape_latex(val)
                    row.append(val)
                tex_table += " & ".join(row) + " \\\\\n\\hline\n"
            tex_table += "\\end{tabularx}\n\\end{center}"

            tex_report = tex_template.replace('{{COMPARISON_TABLE}}', tex_table)
            tex_report = tex_report.replace('{{MEDICAL_CONTENT}}', self.md_to_tex(self.medical_comparison))
            tex_report = tex_report.replace('{{PREGNANCY_CONTENT}}', self.md_to_tex(self.pregnancy_content))
            tex_report = tex_report.replace('{{ORGANS_CONTENT}}', self.md_to_tex(self.organs_proteins))
            tex_report = tex_report.replace('{{APPENDIX_CONTENT}}', self.md_to_tex(self.medications_appendix))

            # Add chemical descriptions
            desc_key = 'description' if lang == 'en' else f'description_{lang}'
            for name, data in self.chemicals.items():
                placeholder = "{{" + name.upper() + "_DESCRIPTION}}"
                description = data.get(desc_key, data.get('description', 'No description available.'))
                tex_report = tex_report.replace(placeholder, self.escape_latex(description))

            with open(output_tex, 'w') as f:
                f.write(tex_report)
            print(f"Generated {output_tex}")

if __name__ == "__main__":
    assembler = Assembler()
    # Generate English report
    assembler.assemble(lang='en')
    # Generate German report
    assembler.assemble(lang='de')
