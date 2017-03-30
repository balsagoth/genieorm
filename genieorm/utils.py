def dict_from_path(dct, path):
    for p in path.split('.'):
        dct = dct[p]
    return dct


def join_path(a, b):
    if not a:
        return b
    return "{0}.{1}".format(a, b)


def dict_value(dct):
    return dct['_value']
