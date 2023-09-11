import json
from os import listdir, path, sep
from uuid import uuid4

from celery.result import AsyncResult
from flask import Flask, redirect, render_template, request, send_file, make_response, url_for

from celery_tasks import celery_app, bg_extract
from utils import clear_directory, find_valid_filename

app = Flask(__name__, static_url_path="/static")
pdf_dir = path.join(path.dirname(path.realpath(__file__)), "src%spdfs" % sep)
pdfs = filter(lambda file: file.endswith(".pdf"), listdir(pdf_dir))
pdfs = list(map(lambda file: file[:-4], pdfs))
pdfs.sort()

result_dir = path.join(path.dirname(path.realpath(__file__)), "src%sresults" % sep)

clear_directory(result_dir)


def save_uploaded(uploaded_file):
    if not uploaded_file.mimetype == "application/pdf":
        print("Mimetype Mismatch: %s" % uploaded_file.mimetype)
        return "Not a PDF", 400

    save_to = find_valid_filename(uploaded_file.filename, pdfs)

    pdfs.append(save_to)
    pdfs.sort()
    save_to = path.join(pdf_dir, save_to + ".pdf")
    uploaded_file.save(save_to)

    return save_to


def process(selected_pdf, page_range):
    selected_path = path.join(pdf_dir, selected_pdf + ".pdf")
    write_to = f"{selected_pdf} - {str(uuid4())}.pdf"

    pdf_extract_task = bg_extract.delay(selected_path, page_range, path.join(result_dir, write_to))

    return pdf_extract_task.task_id


@app.route("/")
def home():
    return render_template("index.html", pdf_list=pdfs)


@app.route("/merge")
def merge():
    return render_template("merge.html", pdf_list=pdfs)


@app.route("/merge/submit", methods=["POST"])
def merge_submit():
    merge_paths = [path.join(pdf_dir, file_name + ".pdf") for file_name in request.form.getlist("selected-pdfs[]")]
    print(merge_paths)
    # TODO: Test merging in Celery then test scheduled merged in Celery
    return make_response("WIP")


@app.route("/submit", methods=["POST"])
def submit():
    page_range = request.form["pageRange"]
    if "selectedPDF" in request.form:
        # TODO: Resolve the path
        selected_pdf = request.form["selectedPDF"]
    else:
        selected_pdf = save_uploaded(request.files["uploadedPDF"])

    pdf_extract_task_id = process(selected_pdf, page_range)
    return url_for("view_status", task_id=pdf_extract_task_id), 202


@app.route("/redirect/<file_name>/<page_range>", methods=["GET"])
def redirect_url(file_name, page_range):
    return redirect("/view/status/%s" % process(file_name, page_range))


@app.route("/view/<file_name>", methods=["GET"])
def view(file_name):
    print("View Requested for %s" % file_name)
    return send_file(path.join(result_dir, file_name), mimetype="application/pdf")


@app.route("/download/<file_name>", methods=["GET"])
def results(file_name):
    print("Download Requested for %s" % file_name)
    # TODO: Delete files after some time
    new_filename = f"{file_name}.pdf"
    file_path = path.join(result_dir, file_name)
    return send_file(file_path, as_attachment=True, download_name=new_filename, mimetype="application/pdf")


@app.route("/view/status/<task_id>", methods=["GET"])
def view_status(task_id):
    return render_template("pdf_status.html", celery_task_id=task_id)


@app.route("/view/status/poll/<task_id>", methods=["GET"])
def view_status_poll(task_id):
    res = AsyncResult(task_id, app=celery_app)
    if res.info is not None and res.status != "SUCCESS":
        response = make_response(json.dumps(res.info), 200)
    elif res.result is not None:
        response = make_response(json.dumps({"result": path.basename(res.result)}), 200)
    else:
        response = make_response(json.dumps({"pending": True}), 200)

    response.mimetype = "application/json"
    return response


if __name__ == "__main__":
    app.run(debug=True)
