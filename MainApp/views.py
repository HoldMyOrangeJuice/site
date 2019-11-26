from django.shortcuts import render
from MainApp.models import Item
import xlrd
# Create your views here.


def start_page(request):

    item_objects = Item.objects.all()

    if request.GET.get("price") == "pressed":
        return render(request, "price_table.html", context={"items": item_objects})
    return render(request, "index.html")


def admin_page(request):

    global file, wb, rows, cols
    if request.method == 'POST':

        if request.FILES.get("file_input"):
            try:
                    file = request.FILES['file_input'].read()

                    print("create table")
                    wb = xlrd.open_workbook(file_contents=file)
                    print(wb, "wb")
                    ws = wb.sheet_by_index(0)

                    table = []
                    cols = ws.ncols  # x
                    rows = ws.nrows  # y
                    print("cols:", ws.ncols, "rows:", ws.nrows)
                    for x in range(ws.nrows):
                        row = []
                        for y in range(ws.ncols):
                            print("cell", ws.cell_value(x, y))
                            row.append(ws.cell_value(x, y))
                        table.append(row)
                        print("row")
                    return render(request, "admin_page.html",
                                  context={"full_price_table": table, "x": list(range(cols)), "y": list(range(rows))})
            except:
                pass

        if request.POST.get("sub_btn") == "pressed":

            print(rows, "rows")
            for r in range(rows):
                for c in range(cols):
                    print(request.POST.get(f"{r}&{c}"))
                    print(request.POST.get(f"{c}-header"))





    return render(request, "admin_page.html")
