from PyPDF2 import PdfWriter, PdfReader
from celery import Celery
import extractPage

celery_app = Celery("celery_hello", broker="redis://localhost/0", backend="redis://localhost/0")


@celery_app.task(bind=True)
def bg_extract(self, pdf_path, page_range, write_to):
    # print("Searching path %s" % path)
    pdf_extract = PdfWriter()
    with open(pdf_path, "rb") as input_file:
        pdf = PdfReader(input_file)
        range_list = extractPage.decompress_range(page_range, len(pdf.pages))
        # pdf_extract.addMetadata({
        #     "/Title": re.search("[\\d\\w]+(?=\\.pdf$)", path, re.IGNORECASE).group(0)
        # })
        self.update_state(state="PROGRESS", meta={"current": 0, "total": len(range_list)})
        for progress, page_num in enumerate(range_list):
            page_extract = pdf.pages[page_num - 1]
            pdf_extract.add_page(page_extract)
            self.update_state(state="PROGRESS", meta={"current": progress, "total": len(range_list)})

    pdf_extract.write(open(write_to, "wb"))
    return write_to
