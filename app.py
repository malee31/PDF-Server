from os import listdir, path, sep
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import extractPage

app = Flask(__name__, static_url_path="/static")
pdf_dir = path.join(path.dirname(path.realpath(__file__)), "src%spdfs" % sep)
pdfs = filter(lambda file: file.endswith(".pdf"), listdir(pdf_dir))
pdfs = list(map(lambda file: file[:-4], pdfs))
pdfs.sort()


@app.route("/")
def home():
	return render_template("index.html", pdf_list=pdfs)


@app.route("/submit", methods=["POST"])
def submit():
	page_range = request.form["pageRange"]
	if "selectedPDF" in request.form:
		# TODO: Resolve the path
		selected_pdf = request.form["selectedPDF"]
	else:
		uploaded_file = request.files["uploadedPDF"]
		if not uploaded_file.mimetype == "application/pdf":
			print("Mimetype Mismatch: %s" % uploaded_file.mimetype)
			return "Not a PDF", 400

		save_to = secure_filename(uploaded_file.filename)
		if save_to.endswith(".pdf"):
			save_to = save_to[:-4]

		if save_to in pdfs:
			if len(save_to) == 0:
				print("Blank File Name Parsed From %s" % uploaded_file.filename)
				save_to = "Temp"
			file_name_counter = 1
			while True:
				if not "%s %d" % (save_to, file_name_counter) in pdfs:
					save_to = "%s (%d)" % (save_to, file_name_counter)
					break
				file_name_counter += 1
				# Arbitrary limit for amount of attempts to find a valid file name
				if file_name_counter > 200:
					raise Exception("Error finding a filename for %s extracted from %s" % (save_to, uploaded_file.filename))

		selected_pdf = save_to
		pdfs.append(save_to)
		pdfs.sort()
		save_to = path.join(pdf_dir, save_to + ".pdf")
		uploaded_file.save(save_to)

	selected_pdf = path.join(pdf_dir, selected_pdf + ".pdf")
	# TODO: Page number parsing and constructing PDF responses
	result_pdf = extractPage.extract_range(selected_pdf, page_range)
	print(result_pdf)
	return "", 200


if __name__ == "__main__":
	app.run(debug=True)
