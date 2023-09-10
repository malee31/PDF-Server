import json
from os import listdir, path, sep, unlink
from shutil import rmtree
from uuid import uuid4

from flask import Flask, redirect, render_template, request, send_file, make_response, url_for
from werkzeug.utils import secure_filename

from celery.result import AsyncResult
from celery_tasks import celery_app, bg_extract

app = Flask(__name__, static_url_path="/static")
pdf_dir = path.join(path.dirname(path.realpath(__file__)), "src%spdfs" % sep)
pdfs = filter(lambda file: file.endswith(".pdf"), listdir(pdf_dir))
pdfs = list(map(lambda file: file[:-4], pdfs))
pdfs.sort()

result_dir = path.join(path.dirname(path.realpath(__file__)), "src%sresults" % sep)


def delete_cached_results():
    for filename in listdir(result_dir):
        delete_path = path.join(result_dir, filename)
        if not delete_path.endswith(".pdf"):
            continue
        try:
            if path.isfile(delete_path) or path.islink(delete_path):
                unlink(delete_path)
            elif path.isdir(delete_path):
                # Likely never going to be called
                rmtree(delete_path)
        except Exception as err:
            print('Failed to delete %s\n%s' % (delete_path, err))


delete_cached_results()


def find_valid_filename(_basename):
    basename = secure_filename(_basename)
    if basename.endswith(".pdf"):
        basename = basename[:-4]

    if int(len(basename)) == 0:
        print("Blank File Name Parsed From %s" % _basename)
        basename = "Temp"

    if basename in pdfs:
        file_name_counter = 1
        while True:
            suggested_file_name = "%s (%d)" % (basename, file_name_counter)
            if suggested_file_name not in pdfs:
                basename = suggested_file_name
                break
            file_name_counter += 1
            # Arbitrary limit for amount of attempts to find a valid file name
            if file_name_counter > 200:
                raise Exception("Error finding a filename for %s extracted from %s" % (basename, _basename))

    return basename


def process(selected_pdf, page_range):
    selected_path = path.join(pdf_dir, selected_pdf + ".pdf")
    write_to = f"{selected_pdf} - {str(uuid4())}.pdf"

    pdf_extract_task = bg_extract.delay(selected_path, page_range, path.join(result_dir, write_to))

    return pdf_extract_task.task_id


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

        save_to = find_valid_filename(uploaded_file.filename)

        selected_pdf = save_to
        pdfs.append(save_to)
        pdfs.sort()
        save_to = path.join(pdf_dir, save_to + ".pdf")
        uploaded_file.save(save_to)

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
