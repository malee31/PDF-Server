PDF Server
=============
Upload PDFs to the Flask server and request specific pages from it through a form or URL

## Page Range Formats
Page ranges are structured in a way similar to printing ranges.<br>
Use a comma-separated list of numbers of number ranges like `1,3,4-9,11` to choose the pages on the pdf to extract.<br>
In the example, pages `1, 3, 4, 5, 6, 7, 8, 9, 11` will be extracted.<br>
There is also a shorthand for "Until the last page". Using `1,10-` for example would return pages 1, 10, 11, 12 and so on until the last page of the selected pdf.<br>
Invalid page numbers will be ignored.

## URL Endpoints
* `/`: The main page. Contains a form that acts as a GUI for selecting PDFs and their page numbers and is the only way to upload your own pdfs
* `/view/<file_name>`: Allows user to view a result page. Does not allow viewing the original pdf
* `/download/<file_name>`: The same as `/view` except it automatically downloads the file onto the user's downloads folder
* `/redirect/<file_name>/<page_range>`: An endpoint that allows a user to generate a pdf from a pre-existing source without using the form. Used as a sharable link