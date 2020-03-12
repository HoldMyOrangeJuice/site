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
from django.template.loader import render_to_string
import datetime
import os




def start_page(request):

    if request.GET.get("get_hints") == "all":
        return ajax_give_hints()

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

    if True or user:

        if request.GET.get("p") and request.is_ajax():
            return ajax_give_table_pages(request)

        elif request.GET.get("p") and not request.is_ajax():
            print("rendering template")
            q = request.GET.get("q")
            p = request.GET.get("p")
            if not q:
                q = " "

            return render(request, "admin_page.html", context={"q": q, "p": p, "headers": e_headers})

        if request.GET.get("del_items"):
            Item.objects.all().delete()
            ItemPage.objects.all().delete()

        # requested table update?
        if request.GET.get("q") and request.is_ajax():
            return ajax_give_table_pages(request)

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
                                    name=validate_name(row[xl_NAME_COL]),  # lang
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

                for item in Item.objects.all():
                    create_item_page(item)

                # after bulk created and items have ids, i can create htmls named with unique id
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

                    print(f"edited {field_edited} with id of {item_id}. new val is {new_value}")

                    item = Item.objects.all().filter(id=item_id)[0]


                        # if name edited => edit name to search
                        # if category edited => category to search

                    if field_edited == "name" and new_value == "":  # if name erased
                        item.delete()

                    elif field_edited == "name" and new_value != "":
                        Item.__setattr__(item, "name", new_value)
                        Item.__setattr__(item, "name_to_search", cstcf(new_value))

                    if field_edited == "category":
                        Item.__setattr__(item, "category", new_value)
                        Item.__setattr__(item, "category_to_search", cstcf(new_value))

                    else:
                        Item.__setattr__(item, field_edited, new_value)
                        item.save()

                        # after this particular item saved, edit last edited
                        item.__setattr__("last_edited", str(datetime.date.today().strftime("%y/%m/%d")))

                # after changes to db made update whole static price table

                with open("templates/datalist.html", "w", encoding="utf8") as datalist:
                    datalist.write(render_to_string("datalist_template.html",
                                                    {"names": Item.objects.all().values_list('name', flat=True)}))

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

    if request.GET.get("p") and request.is_ajax():
        return ajax_give_table_pages(request)

    elif request.GET.get("p") and not request.is_ajax():
        print("rendering template")
        q = request.GET.get("q")
        p = request.GET.get("p")

        if not q:
            q = " "

        return render(request, "price_table.html", context={"q": q, "p": p, "headers": v_headers})

    if request.GET.get("download_price"):
        make_xlsx()
        response = HttpResponse(open("test.xls", mode="rb"), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{1}test.xls"'
        return response
    ###

    # requested table update?
    if request.GET.get("q") and request.is_ajax():
        return ajax_give_table_pages(request)


    if request.GET.get("category"):
        print("returning dynamic cat")
        item_objects = Item.objects.filter(category_to_search__contains=request.GET.get("category"))
        return render(request, "price_table.html", context={"table": list(enumerate(item_objects)),
                                                            "headers": v_headers,
                                                            "fields": list(enumerate(v_fields)),
                                                            "mode": "view"})
    if request.GET.get("search_request"):
        print("returning dynamic req")
        search_request = request.GET.get("search_request")
        table = search(search_request).order_by('index')
        return render(request, "price_table.html", context={"table": list(enumerate(table)),
                                                            "headers": v_headers,
                                                            "fields": list(enumerate(v_fields)),
                                                            "mode": "view",
                                                            "q": search_request})

    print("returning static page")
    #return render(request, "full_price_static.html")
    return render(request, "price_table.html")


def create_item_page(item):

    context = {"item": item, "date": datetime.date.today().strftime("%y/%m/%d")}

    content = render_to_string('item_page_base.html', context)
    with open(f'templates/items/{item.index}.html', 'w', encoding="utf8") as static_file:
        ItemPage.objects.all().filter(index=item.index).delete()
        ItemPage.objects.create(item_name=item.name,
                                index=item.index)
        static_file.write(content)


def show_custom_item_page(request):

    q = request.GET.get("q")
    if Item.objects.all().filter(index=q).filter(is_hidden=False):
        item = Item.objects.all().filter(index=q).filter(is_hidden=False)[0]
        return render(request, 'item_page_base.html', context={"item": item, "date": item.last_edited})
    return render(request, "error_item_page_not_present.html")



    #  TODO
#   split func to change db item pages and func to show them: done
#   make static price list page with links to item pages (update with db update): in progress
