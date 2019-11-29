from django.shortcuts import render
from MainApp.models import Item
import xlrd
import json
from django.contrib.auth import authenticate, login
from django.contrib.postgres.search import SearchVector
# Create your views here.
TO_SHOW_FIELD = 0

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
    if user:
        if request.method == 'POST':
            global cols, rows
            if request.FILES.get("file_input"):
                global cols, rows, ws
                try:
                        global cols, rows
                        file = request.FILES['file_input'].read()

                        wb = xlrd.open_workbook(file_contents=file)
                        ws = wb.sheet_by_index(0)

                        table = []
                        cols = ws.ncols  # x
                        rows = ws.nrows  # y
                        print("colls rows", cols, rows)
                        for x in range(ws.nrows):
                            row = []
                            for y in range(ws.ncols):
                                row.append(ws.cell_value(x, y))
                            table.append(row)

                        return render(request, "admin_page.html",
                                      context={"full_price_table": table, "x": list(range(cols)), "y": list(range(rows))})
                except:
                    pass

            print(rows)
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
                        print("CHANGES", changes)
                        print("worksheet", ws)
                        cell_header = request.POST.get(f"{c}-header")
                        cell_content = ws.cell_value(r, c)

                        if changes.get(f"{r}&{c}"):
                            print("change detected", changes.get(f"{r}&{c}"))
                            single_item[cell_header] = changes.get(f"{r}&{c}")  # change detected
                        else:
                            single_item[cell_header] = cell_content  # without changes
                            print("no changes", cell_header, single_item[cell_header])


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
                    bulk_to_add.append(Item(
                        name=name,
                        name_to_search=cstcf(name),
                        category=cstcf(category),
                        price=price,
                        amount=amount,
                        to_show=To_show,
                        year=year,
                                            )
                                       )
                Item.objects.bulk_create(bulk_to_add)

        return render(request, "admin_page.html")
    return render(request, "denied.html")

def price_page(request):
    #print("price page view called")
    if request.GET.get("search_request"):
        context = search(request.GET.get("search_request"))
    else:
        context = Item.objects.order_by('category')

    return render(request, "price_table.html", context={"items": context})


def search(key):
    key = cstcf(key)
    #print(key)
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
    string = string.lower()
    return string
