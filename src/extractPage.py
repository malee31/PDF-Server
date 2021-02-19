from PyPDF2 import PdfFileReader, PdfFileWriter
import sys

def getInfo(path):
	with open(path, "rb") as file:
		print(PdfFileReader(file).getDocumentInfo())

def extractPage(path, page):
	with open(path, "rb") as file:
		pdf = PdfFileReader(file)
		page = pdf.getPage(page)
		newpdf = PdfFileWriter()
		newpdf.addPage(page)
		newpdf.write(open("test.pdf", "wb"))

if(__name__ == "__main__"):
	getInfo(sys.argv[1])
	extractPage(sys.argv[1], int(sys.argv[2]))
