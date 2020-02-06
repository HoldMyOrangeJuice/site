from django.shortcuts import render
from MainApp.models import Item
import xlrd
import json
from django.contrib.auth import authenticate, login
from django.contrib.postgres.search import SearchVector
from .funcs import *
from MainApp.config import *
from django.utils.encoding import smart_str
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from .resources import ItemRes
from django.core.mail import send_mail
from siteff import settings


def start_page(request):

    item_objects = Item.objects.order_by('category')

    if request.GET.get("price") == "pressed":
        return render(request, "price_table.html", context={"items": item_objects})

    if request.GET.get("item_requested"):
        item_objects = Item.objects.filter(category_to_search__contains=request.GET.get("item_requested"))
        return render(request, "price_table.html", context={"table": list(enumerate(item_objects)),
                                                            "headers": v_headers,
                                                            "fields": list(enumerate(v_fields)),
                                                            "mode": "view"})
    if request.GET.get("search_request"):
        search_request = request.GET.get("search_request")
        table = search(search_request)
        return render(request, "price_table.html", context={"table": list(enumerate(table)),
                                                            "headers": v_headers,
                                                            "fields": list(enumerate(v_fields)),
                                                            "mode": "view"})

    if request.POST.get("username") and request.POST.get("password"):
        print(request.POST.get("username"), request.POST.get("password"))
        global user
        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        print("USER defined", user)
        if user is not None:
            print("USER", user)
            login(request, user)
    try:
        return render(request, "index.html", context={"user": user})
    except:
        return render(request, "index.html", context={"user": None})


def admin_page(request):
    print(user, "<- user")
    if user:
        if request.method == 'POST':
            if request.FILES.get("file_input"):

                file = request.FILES['file_input'].read()
                wb = xlrd.open_workbook(file_contents=file)
                ws = wb.sheet_by_index(2)

                raw_bulk_from_xls = []

                Item.objects.all().delete()

                for x in range(ws.nrows):
                    row = []
                    for y in range(ws.ncols):
                        cell_val = ws.cell_value(x, y)
                        row.append(cell_val)

                    if row[xl_NAME_COL]:    # name present;
                        item = Item(
                                    name=row[xl_NAME_COL],  # lang
                                    name_to_search=cstcf(row[xl_NAME_COL]),
                                    category=row[xl_CATEGORY_COL],
                                    category_to_search=cstcf(row[xl_CATEGORY_COL]),
                                    price=round_val(row[xl_PRICE_COL], 2),
                                    amount=round_val(row[xl_AMOUNT_COL], 0),
                                    is_hidden=False,
                                    year=round_val(row[xl_YEAR_COL], 0),
                                    photo_link=row[xl_PHOTO_COL],
                                    spot=row[xl_SPOT_COL],
                                    sum=row[xl_SUM_COL],
                                    notes=row[xl_NOTES_COL],
                                    index=int(x)
                                    )
                        raw_bulk_from_xls.append(item)

                Item.objects.all().bulk_create(raw_bulk_from_xls)
                table = Item.objects.all()

                return render(request, "admin_page.html",
                              context={"table": enumerate(table),
                                       "headers": e_headers,
                                       "fields": list(enumerate(e_fields)),
                                       "mode": "edit"
                                       })
#

            if request.POST.get("changes"):
                changes = json.loads(request.POST.get("changes"))
                changes_processed = process_changes(changes)
                print(changes_processed)
                for change in changes_processed:

                    item_id = change["id"]
                    field_edited = change["field"]
                    new_value = change["value"]

                    item = Item.objects.all().filter(id=item_id)[0]

                    if field_edited == "name" and new_value == "":  # if name erased
                        item.delete()

                    else:
                        Item.__setattr__(item, field_edited, new_value)
                        item.save()

            if request.POST.get("sub_btn") == "pressed":
                if request.POST.get("changes"):
                    changes = process_changes(json.loads(request.POST.get("changes")))
                    for change in changes:
                        changed_item = Item.objects.all().filter(id=change.id)
                        changed_item.__setattr__(change.field, change.value)
                        changed_item.save()

        if request.GET.get("edit_db_table") == "pressed":

            return render(request, "admin_page.html", context={
                "table": list(enumerate(Item.objects.all())),
                "fields": list(enumerate(e_fields)),
                "headers": e_headers,
                "mode": "edit"
                })
        if request.GET.get("create_xl") == "pressed":

            # EMAIL_HOST_USER = "rastaprices@gmail.com"
            # EMAIL_HOST_PASSWORD = "nzyTMhXv4y"
            # send_mail(
            #     'Subject here',
            #     'Here is the message.',
            #     'from@example.com',
            #     ['to@example.com'],
            #     # auth_user=EMAIL_HOST_USER,
            #     # auth_password=EMAIL_HOST_PASSWORD,
            #     fail_silently=False,
            # )
            make_xlsx()
            response = HttpResponse(open("test.xls", mode="rb"), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="test.xls"'
            return response

        return render(request, "admin_page.html")
    return render(request, "denied.html")


def price_page(request):

    if request.GET.get("download_price"):
        make_xlsx()
        response = HttpResponse(open("test.xls", mode="rb"), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="test.xls"'
        return response

    q = request.GET.get("search_request")
    if q:
        table = search(q)
    else:
        q = ""  # instead of None
        table = Item.objects.order_by('index')

    return render(request, "price_table.html", context={
        "table": list(enumerate(table)),
        "fields": list(enumerate(v_fields)),
        "headers": v_headers,
        "mode": "view",
        "q": q,
        })



