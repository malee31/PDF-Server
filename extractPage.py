import re

from PyPDF2 import PdfReader, PdfWriter


def extract_range(path, page_range, write_to):
    # print("Searching path %s" % path)
    pdf_extract = PdfWriter()
    with open(path, "rb") as file:
        pdf = PdfReader(file)
        range_list = decompress_range(page_range, len(pdf.pages))
        # pdf_extract.addMetadata({
        #     "/Title": re.search("[\\d\\w]+(?=\\.pdf$)", path, re.IGNORECASE).group(0)
        # })
        for page_num in range_list:
            page_extract = pdf.pages[page_num - 1]
            pdf_extract.add_page(page_extract)
        pdf_extract.write(open(write_to, "wb"))


# Converts a range string like "1,2,3-6" to a list like [1, 2, 3, 4, 5, 6]
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
            if int(len(range_edges)) == 1:
                range_edges.append(limit)

            for page_num in range(int(range_edges[0]), int(range_edges[-1]) + 1):
                if page_num <= 0:
                    continue
                if page_num > limit:
                    break
                decompressed.append(page_num)
    return decompressed
