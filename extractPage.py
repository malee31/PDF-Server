import sys
from os import sep

from PyPDF2 import PdfFileReader, PdfFileWriter


def get_info(path):
	with open(path, "rb") as file:
		print(PdfFileReader(file).getDocumentInfo())


def extract_page(path, page):
	with open(path, "rb") as file:
		pdf = PdfFileReader(file)
		page = pdf.getPage(page)
		new_pdf = PdfFileWriter()
		new_pdf.addPage(page)
		new_pdf.write(open("test.pdf", "wb"))


def extract_range(path, page_range, write_to):
	# print("Searching path %s" % path)
	pdf_extract = PdfFileWriter()
	with open(path, "rb") as file:
		pdf = PdfFileReader(file)
		range_list = decompress_range(page_range, pdf.getNumPages())
		for page_num in range_list:
			page_extract = pdf.getPage(page_num - 1)
			pdf_extract.addPage(page_extract)
		pdf_extract.write(open(write_to, "wb"))


def decompress_range(page_range, limit):
	decompressed = []
	separate = page_range.split(",")
	for sub_range in separate:
		sub_range = sub_range.strip()
		if sub_range[0] == "-":
			sub_range = "1" + sub_range

		if "-" not in sub_range:
			sub_range = int(sub_range)
			if sub_range > limit or sub_range <= 0:
				continue
			decompressed.append(int(sub_range))
		else:
			range_edges = sub_range.split("-")
			if len(range_edges) == 1:
				range_edges.append(limit)

			for page_num in range(int(range_edges[0]), int(range_edges[-1]) + 1):
				if page_num <= 0:
					continue
				if page_num > limit:
					break
				decompressed.append(page_num)

	return decompressed


if __name__ == "__main__":
	get_info(sys.argv[1])
	extract_page(sys.argv[1], int(sys.argv[2]))
