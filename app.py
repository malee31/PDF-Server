from os import listdir

from flask import Flask, render_template

app = Flask(__name__, static_url_path="/static")
pdfs = filter(lambda file: file.endswith(".pdf"), listdir("src/pdfs"))
pdfs = list(map(lambda file: file[:-4], pdfs))
pdfs.sort()


@app.route("/")
def home():
	return render_template("index.html", pdf_list=pdfs)


if __name__ == "__main__":
	app.run(debug=True)
