from os import listdir, path, sep
from uuid import uuid4

from flask import Flask, redirect, render_template, request, send_file
from werkzeug.utils import secure_filename

import extractPage

app = Flask(__name__, static_url_path="/static")
pdf_dir = path.join(path.dirname(path.realpath(__file__)), "src%spdfs" % sep)
result_dir = path.join(path.dirname(path.realpath(__file__)), "src%sresults" % sep)
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

	return "/results/%s" % process(selected_pdf, page_range), 200


def process(selected_pdf, page_range):
	selected_path = path.join(pdf_dir, selected_pdf + ".pdf")
	write_to = str(uuid4()) + ".pdf"
	extractPage.extract_range(selected_path, page_range, path.join(result_dir, write_to))
	return write_to


@app.route("/redirect/<file_name>/<page_range>", methods=["GET"])
def redirect_url(file_name, page_range):
	return redirect("/results/%s" % process(file_name, page_range))


@app.route("/results/<file_name>", methods=["GET"])
def results(file_name):
	print(file_name)
	# TODO: Delete files after some time
	return send_file(path.join(result_dir, file_name), as_attachment=True, attachment_filename=file_name + ".pdf", mimetype="application/pdf")


if __name__ == "__main__":
	app.run(debug=True)
