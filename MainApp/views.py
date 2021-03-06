from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from MainApp.models import Item
from MainApp.models import Order
import xlrd
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.postgres.search import SearchVector
from .funcs import *
from MainApp.config import *
from django.utils.encoding import smart_str
from django.http import HttpResponse
from django.http import StreamingHttpResponse

from django.core.mail import send_mail, EmailMessage
from siteff import settings
from django.template.loader import render_to_string
import datetime
import os
import uuid


def superuser_required():
    def wrapper(wrapped):
        class WrappedClass(UserPassesTestMixin, wrapped):
            def test_func(self):
                return self.request.user.is_superuser


def start_page(request):
    user_agent = user_static_prefix(request)
    if request.GET.get("get_hints") == "all":
        return ajax_give_hints()

    try:
        return render(request, f"{user_agent}/index.html", context={"user": request.user})
    except:
        return render(request, f"{user_agent}/index.html", context={"user": None})


@staff_member_required
def admin_page(request):

    if request.GET.get("p") and request.is_ajax():
        return ajax_give_table_pages(request)

    elif request.GET.get("p") and not request.is_ajax():
        q = request.GET.get("q")
        p = request.GET.get("p")
        if not q:
            q = " "

        return render(request, "desktop/admin/admin_page.html", context={"q": q, "p": p, "headers": e_headers})

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
                                price=round_val(row[xl_PRICE_COL], 2, integer=True),
                                amount=round_val(row[xl_AMOUNT_COL], 0, integer=True),
                                is_hidden=False,
                                year=round_val(row[xl_YEAR_COL], 0, integer=False),
                                photo_link=row[xl_PHOTO_COL],
                                spot=row[xl_SPOT_COL],
                                sum=row[xl_SUM_COL],
                                notes=row[xl_NOTES_COL],
                                index=int(x)
                                )
                    raw_bulk_from_xls.append(item)

            Item.objects.all().bulk_create(raw_bulk_from_xls)

            #for item in Item.objects.all():
                #create_item_page(item)

            # after bulk created and items have ids, i can create htmls named with unique id
            table = Item.objects.all()

            return render(request, "desktop/admin/admin_page.html",
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

            # after changes to db made update static datalist

            with open("templates/datalist.html", "w", encoding="utf8") as datalist:
                datalist.write(render_to_string("desktop/datalist_template.html",
                                                {"names": Item.objects.all().values_list('name', flat=True)}))

        if request.POST.get("sub_btn") == "pressed":
            if request.POST.get("changes"):
                changes = process_changes(json.loads(request.POST.get("changes")))
                for change in changes:
                    changed_item = Item.objects.all().filter(id=change.id)
                    changed_item.__setattr__(change.field, change.value)
                    changed_item.save()

    if request.GET.get("edit_db_table") == "pressed":

        return render(request, "desktop/admin_page.html", context={
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

    return render(request, "desktop/admin/admin_page.html")


def price_page(request):
    user_agent = user_static_prefix(request)

    # if request.GET.get("item_index") and request.is_ajax():
    #     item = Item.objects.all().filter(index=request.GET.get("item_index"))
    #     item_map = item_to_map(item, v_fields)
    #
    #     return HttpResponse(json.dumps({"data": item_map}), content_type="application/json")

    if request.GET.get("confirmed"):
        user = get_custom_user(request)
        confirm_order(c=request.GET.get("confirmed"), u=user)

    if request.GET.get('give_me_user_data'):
        return process_user_data_request(request)

    if request.GET.get('action') == "order" and request.is_ajax():
        # requested order
        res = process_user_order(request)
        print(res)
        return res

    if request.GET.get("p") and request.is_ajax():
        return ajax_give_table_pages(request)

    elif request.GET.get("p") and not request.is_ajax():
        q = request.GET.get("q")
        p = request.GET.get("p")

        if not q:
            q = " "

        try:
            return render(request, f"{user_agent}/price_table.html", context=
            {
                "q": q,
                "p": p,
                "headers": v_headers,
                "logged_in": True
            }
            )
        except:
            return render(request, f"{user_agent}/price_table.html", context={"q": q,
                                                                              "p": p,
                                                                              "headers": v_headers,
                                                                              "logged_in": False})

    if request.GET.get("download_price"):
        make_xlsx()
        response = HttpResponse(open("test.xls", mode="rb"), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{1}test.xls"'
        return response

    # requested table update?
    if request.GET.get("q") and request.is_ajax():
        return ajax_give_table_pages(request)

    if request.GET.get("category"):
        item_objects = Item.objects.filter(category_to_search__contains=request.GET.get("category"))
        return render(request, f"{user_agent}/price_table.html", context={"table": list(enumerate(item_objects)),
                                                            "headers": v_headers,
                                                            "fields": list(enumerate(v_fields)),
                                                            "mode": "view"})
    if request.GET.get("search_request"):
        print("returning dynamic req")
        search_request = request.GET.get("search_request")
        table = search(search_request).order_by('index')
        return render(request, f"{user_agent}/price_table.html", context={"table": list(enumerate(table)),
                                                            "headers": v_headers,
                                                            "fields": list(enumerate(v_fields)),
                                                            "mode": "view",
                                                            "q": search_request})

    return render(request, f"{user_agent}/price_table.html")


def show_custom_item_page(request):
    user_agent = user_static_prefix(request)
    q = request.GET.get("q")
    if Item.objects.all().filter(index=q).filter(is_hidden=False):
        item = Item.objects.all().filter(index=q).filter(is_hidden=False)[0]
        return render(request, f'{user_agent}/item_page_base.html', context={"item": item, "date": item.last_edited})
    return render(request, f"{user_agent}/error_item_page_not_present.html")


"""
page where admin can review received orders
"""


@login_required
def admin_order_page(request):

    if request.GET.get("seen_order"):
        order_id = request.GET.get("order_id")
        Order.objects.filter(id=order_id).update(seen=True)

    days = Order.objects.values_list('day', flat=True).distinct()
    data = {}
    for day in days:
        data[day] = Order.objects.all().filter(day=day).order_by('-time')
    return render(request, "desktop/admin/order_page.html", {"days": days, "orders": data})


""" 
page where user can see his orders and their status 
"""


def user_order_page(request):
    user = get_custom_user(request)
    if not user:
        return render(request, "desktop/account/order_page.html", {"no_info_found": True})

    if user:
        days = Order.get_user_orders(user).values_list('day', flat=True).distinct()
        data = {}
        for day in days:
            data[day] = Order.objects.all().filter(customer_id=user.get_id()).filter(day=day).order_by('-time')

        if data != {}:
            return render(request, "desktop/account/order_page.html", {"days": days, "orders": data})
        else:
            return render(request, "desktop/account/order_page.html", {"days": None, "orders": None})
    return render(request, "desktop/account/order_page.html", {"no_info_found": True})


"""
user configuration page
"""


@login_required
def user_page(request):

    if request.GET.get("action") == "logout":
        logout(request)
        return redirect("/")

    if request.is_ajax() and request.GET.get("action") == "sub_to_mailing":
        if request.user.is_confirmed:
            if request.user.is_subbed_to_mailing:
                # user already subbed for mailing and synced
                return HttpResponse(json.dumps({"response": "already_subbed"}), content_type="application/json")
            else:
                request.user.is_subbed_to_mailing = True
                request.user.save()
                return HttpResponse(json.dumps({"response": "subbed_success"}), content_type="application/json")
        else:
            code = str(uuid.uuid1())
            set_user_code(request.user, code)
            send_confirmation_mail(request.user, code, "sub_to_mailing")
            return HttpResponse(json.dumps({"response": "confirm_code_sent"}), content_type="application/json")

    return render(request, f"{user_static_prefix(request)}/account/user_page.html", {"user": request.user})


"""
page for user login
"""


def login_page(request):

    if request.is_ajax() and request.POST.get("username") and request.POST.get("password"):

        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        if user is not None:
            login(request, user)
            return HttpResponse(json.dumps({"response": "success", "redirect": request.POST.get("next")}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"response": "invalid username or password", "redirect": None}), content_type="application/json")

    if not request.user.is_authenticated:
        return render(request, f"{user_static_prefix(request)}/account/login.html")
    return redirect("/")


"""
page for user registration
e-mail username and password required
TODO e-mail validation
"""


def register_page(request):

    print("register request", request.POST)
    if request.is_ajax():
        if request.POST.get("username") != "" and request.POST.get("email") != "" and request.POST.get("password") != "":
            print("field check passed")

            user = register_user(request=request,
                                 username=request.POST.get("username"),
                                 email=request.POST.get("email"),
                                 password=request.POST.get("password"),
                                 phone=request.POST.get("phone"))

            if user == "user_invalid":
                print("user check not passed")
                return HttpResponse(json.dumps({"response": "username is used"}), content_type="application/json")
            if user == "email_invalid":
                print("user check not passed")
                return HttpResponse(json.dumps({"response": "email is used"}), content_type="application/json")
            if user == "phone_invalid":
                print("user check not passed")
                return HttpResponse(json.dumps({"response": "phone is used"}), content_type="application/json")
            else:
                print("user check passed")
                # js will redirect user to his personal page
                return HttpResponse(json.dumps({"response": "success", "redirect": "/accounts/me"}), content_type="application/json")
        else:
            print("field check not passed")
            return HttpResponse(json.dumps({"response": "not all fields are filled"}), content_type="application/json")
    else:
        return render(request, f"{user_static_prefix(request)}/account/register.html")


def confirmation_page(request):
    if request.user.is_authenticated:
        if request.GET.get("code"):
            action = request.GET.get("action")
            if check_user_code(request.user, request.GET.get("code")):
                request.user.is_confirmed = True

                if action == "sub_to_mailing":
                    request.user.is_subbed_to_mailing = True

                request.user.save()

                return render(request, f"{user_static_prefix(request)}/account/confirm.html", {"status": "success"})
            else:
                return render(request, f"{user_static_prefix(request)}/account/confirm.html", {"status": "fail"})
        else:
            return redirect("/")
    else:
        return render(request, f"{user_static_prefix(request)}/account/confirm.html", {"status": "info"})


@login_required
def chatView(request):
    return render(request, f"{user_static_prefix(request)}/account/chat.html")