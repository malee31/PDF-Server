from os import path, unlink, listdir
from shutil import rmtree

from werkzeug.utils import secure_filename


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


def debug_celery_update_state(*args, **kwargs):
    if len(args):
        print(args)
    if len(kwargs):
        print(kwargs)


def choose_update_state_func(celery_task=None):
    if celery_task is not None:
        return celery_task.update_state
    return debug_celery_update_state


def clear_directory(dir_path):
    for filename in listdir(dir_path):
        delete_path = path.join(dir_path, filename)
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


def find_valid_filename(_basename, existing_files):
    basename = secure_filename(_basename)
    if basename.endswith(".pdf"):
        basename = basename[:-4]

    if int(len(basename)) == 0:
        print("Blank File Name Parsed From %s" % _basename)
        basename = "Temp"

    if basename in existing_files:
        file_name_counter = 1
        while True:
            suggested_file_name = "%s (%d)" % (basename, file_name_counter)
            if suggested_file_name not in existing_files:
                basename = suggested_file_name
                break
            file_name_counter += 1
            # Arbitrary limit for amount of attempts to find a valid file name
            if file_name_counter > 200:
                raise Exception("Error finding a filename for %s extracted from %s" % (basename, _basename))

    return basename
