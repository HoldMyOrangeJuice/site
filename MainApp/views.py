from django.shortcuts import render
from MainApp.models import Item
import xlrd
from django.contrib.postgres.search import SearchVector
# Create your views here.


def start_page(request):

    item_objects = Item.objects.order_by('category')

    if request.GET.get("price") == "pressed":
        return render(request, "price_table.html", context={"items": item_objects})

    if request.GET.get("item_requested"):
        print("item req", request.GET.get("item_requested"))
        item_objects = Item.objects.filter(category=request.GET.get("item_requested"))
        return render(request, "price_table.html", context={"items": item_objects})

    if request.GET.get("search_request"):
        search_request = request.GET.get("search_request")
        query = search(search_request)
        return render(request, "price_table.html", context={"items": query})

    if request.GET.get("contacts") == "pressed":
        return render(request, )

    return render(request, "index.html")


def admin_page(request):

    global file, wb, rows, cols
    if request.method == 'POST':

        if request.FILES.get("file_input"):
            try:
                    file = request.FILES['file_input'].read()

                    wb = xlrd.open_workbook(file_contents=file)
                    ws = wb.sheet_by_index(0)

                    table = []
                    cols = ws.ncols  # x
                    rows = ws.nrows  # y
                    for x in range(ws.nrows):
                        row = []
                        for y in range(ws.ncols):
                            row.append(ws.cell_value(x, y))
                        table.append(row)

                    return render(request, "admin_page.html",
                                  context={"full_price_table": table, "x": list(range(cols)), "y": list(range(rows))})
            except:
                pass

        if request.POST.get("sub_btn") == "pressed":
            bulk_to_add = []
            print(request.POST, "requsest-------")
            for r in range(rows):
                single_item = {}
                To_show = True
                for c in range(cols):
                    cell_header = request.POST.get(f"{c}-header")
                    cell_content = request.POST.get(f"{r}&{c}")
                    print(repr(cell_content), f"in cell {r}&{c}")

                    single_item[cell_header] = cell_content

                if request.POST.get(f"{r}-To_show") == "false":
                    To_show = False
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


def price_page(request):
    print("price page view called")
    if request.GET.get("search_request"):
        context = search(request.GET.get("search_request"))
    else:
        context = Item.objects.order_by('category')

    return render(request, "price_table.html", context={"items": context})


def search(key):
    key = cstcf(key)
    print(key)
    print(Item.objects.all().filter(name_to_search__contains="диод"))
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
