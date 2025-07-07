from datetime import date
from typing import Literal
from fpdf import FPDF, XPos, YPos

class Data:
	def __init__(self, 
			  title: str, 
			  description: str, 
			  link: str, 
			  status: Literal["fail", "success", "normal"]
			):
		self.title = title
		self.description = description
		self.link = link
		self.status = status

class PDFData:
	def __init__(self, title: str, date: date):
		self.title = title
		self.date = date
		self.data = []
	def append(self, data: Data):
		self.data.append(data)
	def set(self, data: list[Data]):
		self.data = data
	def create(self, filename="output.pdf"):
		pdf = FPDF(orientation="portrait", format="A4")
		pdf.add_page()

		pdf.set_font("Courier", size=24)
		pdf.cell(text=f"{self.title}\n", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
		pdf.set_font("Courier", size=14)
		pdf.cell(text=self.date.strftime("%Y/%m/%d"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
		
		with pdf.text_columns() as columns:
			with columns.paragraph(
				text_align="J",
				top_margin=pdf.font_size,
				bottom_margin=pdf.font_size
			) as paragraph:
				for data in self.data:
					#print(data.title)
					if data.status == "success":
						pdf.set_text_color(r=0, g=255, b=0)
					else:
						pdf.set_text_color(r=255, g=0, b=0)
					pdf.set_font(size=14, style="B")
					paragraph.write(data.title + "\n")
					pdf.set_font(size=12)
					paragraph.write(data.description + "\n"*2)
		
		pdf.output(filename)

if __name__ == "__main__":
	pdf = PDFData("Teszt riport", date.today())
	pdf.set([
		Data(title="Budapest Park", description="A helyszín már szerepel az adatbázisban.", link="https://www.tivornya.hu", status="success"),
		Data(title="Petofi Irodalmi Múzeum", description="A helyszín nem szerepel az adatbázisban.", link="https://www.tivornya.hu", status="fail")
	])
	pdf.create()
	
