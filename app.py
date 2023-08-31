import json
from os import listdir, path, sep, unlink
from shutil import rmtree
from uuid import uuid4

from flask import Flask, redirect, render_template, request, send_file, make_response
from werkzeug.utils import secure_filename

import extractPage
from celery_tasks import celery_app, hello
from celery.result import AsyncResult

app = Flask(__name__, static_url_path="/static")
pdf_dir = path.join(path.dirname(path.realpath(__file__)), "src%spdfs" % sep)
pdfs = filter(lambda file: file.endswith(".pdf"), listdir(pdf_dir))
pdfs = list(map(lambda file: file[:-4], pdfs))
pdfs.sort()

result_dir = path.join(path.dirname(path.realpath(__file__)), "src%sresults" % sep)
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

cache = {}
original_filenames = {}


@app.route("/")
def home():
    return render_template("index.html", pdf_list=pdfs)


@app.route("/celery_hello")
def celery_hello():
    res = hello.delay()
    return render_template("celery_hello.html", celery_task_id=res.task_id)


@app.route("/celery_hello/status/<task_id>")
def celery_hello_status(task_id):
    print(hello)
    return render_template("celery_hello.html", celery_task_id=task_id)


@app.route("/celery_hello/<task_id>")
def celery_hello_progress(task_id):
    res = AsyncResult(task_id, app=celery_app)
    response = make_response(json.dumps(res.info), 200)
    response.mimetype = "text/plain"
    return response



@app.route("/celery_hello/end/<task_id>")
def celery_hello_fin(task_id):
    res = AsyncResult(task_id, app=celery_app)
    res.get()
    response = make_response(json.dumps(res.result), 200)
    response.mimetype = "text/plain"
    return response


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
            if int(len(save_to)) == 0:
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
                    raise Exception(
                        "Error finding a filename for %s extracted from %s" % (save_to, uploaded_file.filename))

        selected_pdf = save_to
        pdfs.append(save_to)
        pdfs.sort()
        save_to = path.join(pdf_dir, save_to + ".pdf")
        uploaded_file.save(save_to)

    return process(selected_pdf, page_range), 200


def process(selected_pdf, page_range):
    if selected_pdf not in cache:
        cache[selected_pdf] = {}
    if page_range not in cache[selected_pdf]:
        selected_path = path.join(pdf_dir, selected_pdf + ".pdf")
        write_to = str(uuid4()) + ".pdf"
        extractPage.extract_range(selected_path, page_range, path.join(result_dir, write_to))
        cache[selected_pdf][page_range] = write_to
        original_filenames[write_to] = selected_pdf

    return cache[selected_pdf][page_range]


@app.route("/redirect/<file_name>/<page_range>", methods=["GET"])
def redirect_url(file_name, page_range):
    return redirect("/results/%s" % process(file_name, page_range))


@app.route("/download/<file_name>", methods=["GET"])
def results(file_name):
    print("Download Requested for %s" % file_name)
    # TODO: Delete files after some time
    new_filename = (original_filenames[file_name] if file_name in original_filenames else file_name) + ".pdf"
    file_path = path.join(result_dir, file_name)
    return send_file(file_path, as_attachment=True, download_name=new_filename, mimetype="application/pdf")


@app.route("/view/<file_name>", methods=["GET"])
def view(file_name):
    print("View Requested for %s" % file_name)
    return send_file(path.join(result_dir, file_name), mimetype="application/pdf")


if __name__ == "__main__":
    app.run(debug=True)
