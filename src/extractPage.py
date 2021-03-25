import sys

from PyPDF2 import PdfFileReader, PdfFileWriter


def get_info(path):
	with open(path, "rb") as file:
		print(PdfFileReader(file).getDocumentInfo())


def extract_page(path, page):
	with open(path, "rb") as file:
		pdf = PdfFileReader(file)
		page = pdf.getPage(page)
		newpdf = PdfFileWriter()
		newpdf.addPage(page)
		newpdf.write(open("test.pdf", "wb"))


if __name__ == "__main__":
	get_info(sys.argv[1])
	extract_page(sys.argv[1], int(sys.argv[2]))
