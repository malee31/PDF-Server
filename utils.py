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
