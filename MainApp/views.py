from django.shortcuts import render
from MainApp.models import Item
import xlrd
import json
from django.contrib.auth import authenticate, login
from django.contrib.postgres.search import SearchVector

TO_SHOW_FIELD = 0
NAME_COL      = 1
PRICE_COL     = 2
AMOUNT_COL    = 3
YEAR_COL      = 4

def start_page(request):
    global user
    item_objects = Item.objects.order_by('category')

    if request.GET.get("price") == "pressed":
        return render(request, "price_table.html", context={"items": item_objects})

    if request.GET.get("item_requested"):
        #print("item req", request.GET.get("item_requested"))
        item_objects = Item.objects.filter(category=request.GET.get("item_requested"))
        return render(request, "price_table.html", context={"items": item_objects})

    if request.GET.get("search_request"):
        search_request = request.GET.get("search_request")
        query = search(search_request)
        return render(request, "price_table.html", context={"items": query})


    if request.POST.get("username") and request.POST.get("password"):
        print(request.POST.get("username"), request.POST.get("password"))
        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        print("USER", user)
        if user is not None:
            print("USER", user)
            login(request, user)

    return render(request, "index.html")


def admin_page(request):
    global cols, rows
    if True or user:
        if request.method == 'POST':
            global cols, rows
            if request.FILES.get("file_input"):
                        global cols, rows, ws
                #try:
                        global cols, rows

                        file = request.FILES['file_input'].read()

                        wb = xlrd.open_workbook(file_contents=file)
                        ws = wb.sheet_by_index(0)
                        item_changes = {}
                        table = []
                        cols = ws.ncols  # x
                        rows = ws.nrows  # y 4
                        print("colls rows", cols, rows)
                        for x in range(ws.nrows):
                            row = []
                            conclusion = []
                            for y in range(ws.ncols):
                                cell_val = ws.cell_value(x, y)
                                row.append(cell_val)
                                print("col number", y, "height", x)

                                if y == NAME_COL:
                                    item_names_in_db = []
                                    try:
                                        item_names_in_db = Item.objects.all().filter(name=cell_val)
                                        print(cell_val, "ITEM IN DATABASE")
                                    except:
                                        print(cell_val, "ITEM WITH THIS NAME IS NOT PRESENT IN DATABASE")

                                    if len(item_names_in_db) > 0:

                                        db_amounts = []
                                        db_prices = []
                                        db_years = []

                                        ws_amount = cstcf(ws.cell_value(x, AMOUNT_COL))
                                        ws_price = cstcf(ws.cell_value(x, PRICE_COL))
                                        ws_year = cstcf(ws.cell_value(x, YEAR_COL))

                                        for item_in_db in item_names_in_db:
                                            db_amounts.append(cstcf(item_in_db.amount))
                                            db_prices.append(cstcf(item_in_db.price))
                                            db_years.append(cstcf(item_in_db.year))

                                        if ws_price in db_prices and ws_amount in db_amounts and ws_year in db_years:

                                            conclusion.append("not_changed")   # item not changed

                                        else:

                                            if ws_price not in db_prices:
                                                print("price1", ws_price, "price2", db_prices)
                                                conclusion.append("price_changed")

                                            if ws_amount not in db_amounts:
                                                conclusion.append("amount_changed")
                                                print("am1", ws_amount, "am2", db_amounts,"\n",
                                                      repr(ws_amount), repr(db_amounts) )

                                            if ws_year not in db_years:
                                                print("y1", ws_year, "y2", db_years)
                                                conclusion.append("year_changed")

                                    else:
                                        conclusion.append("new_item")

                                item_changes[x] = conclusion
                                #Item.objects.all().filter(name=cell_val).delete()


                            table.append(row)
                        hidden_query = Item.objects.all().filter(to_show=False).values_list("name", flat=True)
                        print(hidden_query)
                        return render(request, "admin_page.html",
                                      context={"full_price_table": table,
                                               "x": list(range(cols)),
                                               "y": list(range(rows)),
                                               "item_changes": json.dumps(item_changes),
                                               "hidden_item_names": hidden_query,
                                               })
                #except:
                    #pass

            if request.POST.get("changes_to_db_table"):
                changes = json.loads(request.POST.get("changes_to_db_table"))
                print(changes)
                keys = changes.keys()
                for key in keys:
                    new_value = changes[key]
                    item_id = key.split("|")[0]
                    field_edited = key.split("|")[1]

                    item = Item.objects.all().filter(id=item_id)[0]  # table uses name, not name_to_search
                    if field_edited == "to_show":

                        new_value = (new_value == "true")
                        print("old val", Item.__getattribute__(item, "to_show"), "new val", new_value)

                    print(new_value)
                    Item.__setattr__(item, field_edited, new_value)
                    item.save()

            if request.POST.get("sub_btn") == "pressed":
                changes = {}
                if request.POST.get("changes"):
                    changes = json.loads(request.POST.get("changes"))

                bulk_to_add = []
                for r in range(rows):
                    single_item = {}
                    To_show = True
                    if changes.get(f"{r}-To_show") and changes.get(f"{r}-To_show") == "false":
                        To_show = False

                    for c in range(cols):

                        cell_header = request.POST.get(f"{c}-header")
                        cell_content = ws.cell_value(r, c)

                        if changes.get(f"{r}a{c}"):
                            print("change detected", changes.get(f"{r}a{c}"))
                            single_item[cell_header] = changes.get(f"{r}a{c}")  # change detected
                        else:
                            single_item[cell_header] = cell_content  # without changes
                            #print("no changes", cell_header, single_item[cell_header])


                    if single_item.get("Name"):
                        name = single_item.get("Name")
                    else:
                        name = "-"
                    if single_item.get("Price"):
                        price = single_item.get("Price")
                    else:
                        price = "-"
                    if single_item.get("Amount"):
                        amount = single_item.get("Amount")
                    else:
                        amount = "-"
                    if single_item.get("Year"):
                        year = single_item.get("Year")
                    else:
                        year = "-"
                    if single_item.get("Group"):
                        category = single_item.get("Group")
                    else:
                        category = "-"

                    photo_link = single_item.get("photo link")  # including none
                    print(photo_link)

                    Item.objects.all().filter(name_to_search=cstcf(name),
                                              category=cstcf(category),
                                              ).delete()
                    # deleting old item before adding new one

                    bulk_to_add.append(Item(
                        name=name,  # lang
                        name_to_search=cstcf(name),
                        category=cstcf(category),
                        price=price,
                        amount=amount,
                        to_show=To_show,
                        year=year,
                        photo_link=photo_link,
                                            )
                                       )
                Item.objects.bulk_create(bulk_to_add)
        if request.GET.get("edit_db_table") == "pressed":
            fields = []
            for field in Item._meta.fields:
                if field.name != "name_to_search" and field.name != "id" and field.name != "to_show" and field.name != "photo_link":
                    fields.append(field.name)
            return render(request, "admin_page.html", context={
                "current_price_list": enumerate(Item.objects.all()),
                "fields": fields
                })
        return render(request, "admin_page.html")
    return render(request, "denied.html")

def price_page(request):
    #print("price page view called")
    if request.GET.get("search_request"):
        context = search(request.GET.get("search_request"))
    else:
        context = Item.objects.order_by('category')

    return render(request, "price_table.html", context={"items_enumed": enumerate(context)})


def search(key):
    key = cstcf(key)

    #print(Item.objects.all().filter(name_to_search__contains="диод"))
    query1 = Item.objects.all().filter(name_to_search__contains=key)
    query2 = Item.objects.all().filter(category__contains=key)
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
