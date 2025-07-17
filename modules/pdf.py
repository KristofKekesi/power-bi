from datetime import date
from typing import Literal
from fpdf import FPDF, XPos, YPos
from urllib.parse import urlparse
from modules.custom_logger import CustomLogger

class Data:
	def __init__(self, 
			  title: str, 
			  description: str, 
			  link: str, # list[str]
			  status: Literal["fail", "success", "normal"]
			):
		self.title = title
		self.description = description
		self.link = link
		self.status = status

class Title:
	def __init__(self, title: str):
		self.title = title

class PDFData:
	def __init__(self, title: str, date: date):
		self.logger = CustomLogger("PDFGenerator")
		self.title = title
		self.date = date
		self.data = []
	def append(self, data: Data):
		self.data.append(data)
	def set(self, data: list[Data]):
		self.data = data
	def create(self, filename="output.pdf"):
		self.logger.info(f"Generating PDF to {filename}")

		RED800   = {"r": 159, "g":   7, "b":  18}
		GREEN800 = {"r":  60, "g":  99, "b":   0}
		BLACK    = {"r":   0, "g":   0, "b":   0}

		pdf = FPDF(orientation="portrait", format="A4")
		pdf.add_page()

		pdf.set_font("Courier", size=24)
		pdf.cell(text=f"{self.title}\n", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
		pdf.set_font("Courier", size=14)
		pdf.cell(text=self.date.strftime("%Y/%m/%d"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
		
		for data in self.data:
			if isinstance(data, Data):
				with pdf.text_columns() as columns:
					with columns.paragraph(
						text_align="J",
						top_margin=pdf.font_size,
						bottom_margin=pdf.font_size
					) as paragraph:
						match data.status:
							case "success": color = GREEN800
							case "fail": color = RED800
							case _: color = BLACK
						pdf.set_text_color(**color)
						pdf.set_font(size=14, style="B")
						paragraph.write(data.title + "\n")
						pdf.set_font(size=12)
						paragraph.write(data.description)
				pdf.set_font(size=12, style="")
				pdf.write(text=f"{urlparse(data.link).hostname} {"\n"*2}", link=data.link)
			if isinstance(data, Title):
				with pdf.text_columns() as columns:
					with columns.paragraph(
						text_align="J",
						top_margin=pdf.font_size,
						bottom_margin=pdf.font_size
					) as paragraph:
						pdf.set_text_color(**BLACK)
						pdf.set_font(size=18)
						paragraph.write(text=f"{data.title}\n")
		pdf.output(filename)

if __name__ == "__main__":
	pdf = PDFData("Teszt riport", date.today())
	pdf.set([
		Data(
			title="Budapest Park", 
			description="A helyszín már szerepel az adatbázisban.", 
			link="https://www.tivornya.hu", 
			status="success"
		),
		Data(
			title="Petofi Irodalmi Múzeum", 
			description="A helyszín nem szerepel az adatbázisban.", 
			link="https://www.tivornya.hu", 
			status="fail"
		)
	])
	pdf.create()
	
