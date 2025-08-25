from latex import build_pdf

class PdfGenerator:
	def __init__(self): pass

	def chart(self, data):
		"""
		A chart making function.
		"""
    
		# Extract data components
		title = data.get("title", "")
		ylabel = data.get("ylabel", "")
		formatting = data.get("formatting", {})
		values = data.get("values", [])
		
		# Build the LaTeX string
		latex_lines = []
		
		# Start the tikzpicture and axis
		latex_lines.extend([
			r"\begin{center}",
			r"\begin{tikzpicture}",
			r"\begin{axis}[",
			r"    ybar stacked,",
			f"    title={{{title}}},",
			r"    xlabel={},",
			f"    ylabel={{{ylabel}}},",
		])
		
		# Build symbolic x coords from labels
		labels = [val.get("label", "") for val in values]
		symbolic_coords = ", ".join(labels)
		latex_lines.append(f"    symbolic x coords={{{symbolic_coords}}},")
		
		latex_lines.extend([
			r"    xtick=data,",
			r"    xticklabel style={rotate=45, anchor=north east},",
			r"    legend style={",
        	r"        at={(0.5,-0.4)},",
			r"        anchor=north,",
    		r"    },",
			r"    bar width=20pt,",
			r"]",
			r"",  # Empty line after axis parameters
		])
		
		# Add plots for each series
		for key, format_info in formatting.items():
			fill_color = format_info.get("fill", "")
			latex_lines.append(f"\\addplot[fill={fill_color}] coordinates {{")
			
			# Add coordinates for this series
			for val in values:
				label = val.get("label", "")
				value = val.get(key, 0)
				latex_lines.append(f"    ({label}, {value}) ")
			
			latex_lines.extend([
				"};",
				""  # Empty line after each addplot
			])
		
		# Add legend
		legend_entries = [format_info.get("legend", "") for format_info in formatting.values()]
		legend_str = ", ".join(legend_entries)
		latex_lines.append(f"\\legend{{{legend_str}}}")
		
		# Close the axis and tikzpicture
		latex_lines.extend([
			r"\end{axis}",
			r"\end{tikzpicture}",
			r"\end{center}"
		])
		
		return "\n".join(latex_lines)

	def create(self, latex_code: str, output: str="output.pdf"):
		pdf = build_pdf(latex_code)
		pdf.save_to(output)


if __name__ == "__main__":
	pdf = PdfGenerator()

	latex_code = fr"""
	\documentclass{{article}}

	\usepackage{{graphicx}}
	\usepackage[magyar]{{babel}}
	\usepackage{{pgfplots}}
	\usepackage{{t1enc}}

	\pgfplotsset{{compat=1.18}}

	\begin{{document}}
	Hello World!
	{pdf.chart({
		"title": "Example chart",
		"ylabel": "Y Label",
		"formatting": {
			"A": {"fill": "red!70",  "legend": "Aa"},
			"B": {"fill": "blue!70", "legend": "Bb"},
			"C": {"fill": "orange!70", "legend": "Bb"},
		},
		"values": [
			{"A": 1, "B": 2, "C": 3, "label": "Column 1."},
			{"A": 3, "B": 4, "C": 32, "label": "Column 2."},
			{"A": 3, "B": 4, "C": 32, "label": "Column 3."}
		]
	})}
	\end{{document}}
	"""
	
	pdf.create(latex_code)
	
