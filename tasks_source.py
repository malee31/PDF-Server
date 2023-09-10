# Converts a range string like "1,2,3-6" to a list like [1, 2, 3, 4, 5, 6]
import os.path
import re
import time
from PyPDF2 import PdfWriter, PdfReader

from utils import decompress_range, choose_update_state_func


def bg_extract(pdf_path, page_range, write_to, *, celery_task=None):
    # Celery progress updater that prints instead when debugging
    update_state = choose_update_state_func(celery_task)

    # print("Searching path %s" % pdf_path)
    pdf_extract = PdfWriter()
    with open(pdf_path, "rb") as input_file:
        pdf = PdfReader(input_file)
        range_list = decompress_range(page_range, len(pdf.pages))
        pdf_extract.add_metadata({
            "/Title": pdf.metadata.title or re.search(r'[^\\/]+(?=\.pdf$)', pdf_path, re.IGNORECASE).group(0)
        })
        update_state(state="PROGRESS", meta={"current": 0, "total": len(range_list)})
        for progress, page_num in enumerate(range_list):
            page_extract = pdf.pages[page_num - 1]
            pdf_extract.add_page(page_extract)
            update_state(state="PROGRESS", meta={"current": progress, "total": len(range_list)})

    update_state(state="PROGRESS", meta={"current": len(range_list), "total": len(range_list)})
    pdf_extract.write(open(write_to, "wb"))
    return os.path.basename(write_to)
