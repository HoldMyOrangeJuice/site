from MainApp.models import Item
import xlwt
from .config import *


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


def cstcf(string):
    string = str(string)
    string = string.replace(" ", "")
    string = string.replace("-", "")
    string = string.replace(" ", "")
    string = string.upper()

    rus = ["А", "В", "С", "Е", "Р", "У", "К", "Н", "Х", "М", "Т"]
    eng = ["A", "B", "C", "E", "P", "Y", "K", "H", "X", "M", "T"]

    if len(rus) == len(eng):
        for i in range(len(rus)):

            string = string.replace(eng[i], rus[i])

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
