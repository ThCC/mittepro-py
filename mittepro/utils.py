import json


def is_json(value):
    try:
        parsed = json.loads(value)
        return True
    except Exception:
        return False


def merge_two_dicts(d1, d2):
    d3 = d1.copy()
    d3.update(d2)
    return d3


def item_in_dict(dictionary, item):
    return item in dictionary and dictionary[item]


def item_not_in_dict(dictionary, item):
    return item not in dictionary or not dictionary[item]


def attr_in_instance(instance, attr):
    return hasattr(instance, attr) and getattr(instance, attr)


def attr_not_in_instance(instance, attr):
    return not hasattr(instance, attr) or not getattr(instance, attr)
