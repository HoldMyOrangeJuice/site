from MainApp.models import Item
from MainApp.models import ItemPage
import xlwt
from .config import *
import json


def get_model_fields_except(exceptions):
    fields = []
    for field in Item._meta.fields:
        field = field.name
        if field not in exceptions:
            fields.append(field)
    return fields


def process_changes(changes):
    value = ""
    id_ = ""
    field_changed = ""
    processed = []
    keys = changes.keys()
    for key in keys:
        value = changes[key]
        id_ = key.split("|")[0]
        field_changed = key.split("|")[1]
        change = {"id": id_, "field": field_changed, "value": value}
        processed.append(change)
    return processed

def search(key):
    key = cstcf(key)

    query1 = Item.objects.all().filter(name_to_search__contains=key)
    query2 = Item.objects.all().filter(category_to_search__contains=key)
    query = query1 | query2
    return query


def fix_lang(string):
    string = str(string)
    rus = ["А", "В", "С", "Е", "Р", "У", "К", "Н", "Х", "М", "Т", "О"]
    eng = ["A", "B", "C", "E", "P", "Y", "K", "H", "X", "M", "T", "O"]

    if len(rus) == len(eng):
        for i in range(len(rus)):
            string = string.replace(eng[i].upper(), rus[i].upper())
            string = string.replace(eng[i].lower(), rus[i].lower())

    return string


def validate_name(name):

    return fix_symbols(fix_lang(name))


def fix_symbols(string):

    string = str(string)
    string = string.replace("\\", "")
    string = string.replace("/", "")
    string = string.replace("*", "")
    string = string.replace("?", "")
    string = string.replace("<", "")
    string = string.replace(">", "")
    string = string.replace(":", "")
    string = string.replace("|", "")
    string = string.replace("'", "")
    string = string.replace("\"", '')


    return string


def cstcf(string):
    string = str(string)
    string = string.replace(" ", "")
    string = string.replace("-", "")
    string = string.replace(" ", "")

    string = fix_symbols(string)
    string = string.upper()
    fix_lang(string)
    string = string.lower()
    return string


def make_xlsx():
    items = Item.objects.all().filter(is_hidden=False)
    book = xlwt.Workbook()
    sheet1 = book.add_sheet("Прайс")
    for c in range(xl_marg_left, len(v_headers) + xl_marg_left):
        col = sheet1.col(c)
        col.width = 256 * 20
    for col, header in enumerate(v_headers):

        if header != "№":
            row = sheet1.row(xl_marg_top_headers)

            row.write(xl_marg_left + col, header)

    for row_index, item in enumerate(items):
        row = sheet1.row(xl_marg_top + row_index)
        for col_index, col in enumerate(v_fields):
            if col != "number":
                row.write(xl_marg_left + col_index, item.__getattribute__(col))
    book.save("test.xls")


def round_val(val, n):
    if val:
        if n == 0:
            try:
                val = int(val)
            except:
                pass
        else:

            try:
                val = round(float(val), n)
            except:
                pass
    return val


def item_to_obj(item_query, fields):
    r = []

    for item in item_query:
        i = {}
        for field in fields:
            i[field] = getattr(item, field)
        # also adding id
        i["id"] = item.id

        r.append(i)
    return r


