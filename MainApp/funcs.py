import datetime

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.template.loader import render_to_string

from MainApp.models import Item, Customer, TempUser
from MainApp.models import Order
from MainApp.models import ItemPage
import xlwt
from .config import *
import json
from django.http import HttpResponse
import math
from difflib import SequenceMatcher


USER_CODES = {}


def get_model_fields_except(exceptions):
    fields = []
    for field in Item._meta.fields:
        field = field.name
        if field not in exceptions:
            fields.append(field)
    return fields


def process_changes(changes):
    processed = []
    keys = changes.keys()
    for key in keys:
        value = changes[key]
        id_ = key.split("|")[0]
        field_changed = key.split("|")[1]
        change = {"id": id_, "field": field_changed, "value": value}
        processed.append(change)
    return processed


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def search(q):
    keywords = split_keywords(q)
    key = cstcf(q)
    reg = {}
    resp_q = []
    for item in Item.objects.all():

        weight = similar(key, item.name_to_search)

        keywords_found_count = 0
        for keyword in keywords:
            keyword = cstcf(keyword)
            if keyword in item.name_to_search or keyword in item.category_to_search:
                keywords_found_count += 1

        q_keyword_price = keywords_found_count / len(keywords)
        weight = weight + ((1-weight)*q_keyword_price)

        if reg.get(weight):
            exs = reg[weight]
            exs.append(item)
            reg[weight] = exs
        else:
            reg[weight] = [item]

    weights = reg.keys()
    weights = sorted(weights)

    for weight in weights[::-1]:
        if weight > 0.5 and (len(resp_q) < 25 or weight > 0.8):
            resp_q.extend(reg[weight])
        else:
            break

    return resp_q


def split_keywords(q):
    q = q.replace("-", " ")
    keywords = q.split(" ")
    return keywords


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

    return fix_symbols(name)


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
    string = string.replace(",", '')
    string = string.replace(".", '')

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


def round_val(val, n, integer):

    if not integer:
        default = "-"
    else:
        default = 0
    if val:
        if n == 0:
            try:
                val = int(val)
                return val
            except:
                return default
        else:

            try:
                val = round(float(val), n)
                return val
            except:
                return default
    else:
        return default


def item_to_map(item_query, fields):
    r = {}

    for item in item_query:
        i = {}
        for field in fields:
            i[field] = getattr(item, field)

        r[item.id] = i
    return r


def ajax_give_table_pages(request):

    page_index = int(request.GET.get("p"))
    item_req = request.GET.get("q")
    items_on_page = 200

    admin = "adm" in request.build_absolute_uri()
    if admin:
        headers = e_field_headers
    else:
        headers = v_field_headers

    full_query = search(item_req)
    if item_req == "":
        full_query = Item.objects.all()

    if page_index * items_on_page > len(full_query):
        # page does not exist, no items left
        return HttpResponse(json.dumps({"query": [],
                                        "headers": [],
                                        "max-pages": math.ceil(len(full_query)/items_on_page),
                                        "entries": len(full_query)}),
                                         content_type="application/json")

    query = full_query[page_index * items_on_page: min((page_index + 1) * items_on_page, len(Item.objects.all()) - 1)]
    query = item_to_map(query, headers)

    return HttpResponse(json.dumps({"query": query,
                                    "headers": headers,
                                    "max-pages": math.ceil(math.ceil(len(full_query) / items_on_page)),
                                    "entries": len(full_query)}),
                                     content_type="application/json")


# no need in this one.
def ajax_update_table(request):

    admin = "adm" in request.build_absolute_uri()
    if admin:
        headers = e_field_headers
    else:
        headers = v_field_headers

    item_req = request.GET.get("q")

    if item_req == "give_me_full_table":
        query = Item.objects.all()

    else:
        query = search(item_req)
        query = query[0:min(500, len(query))]

    hints = []
    for hint in query[:min(10, len(query))]:
        hints.append(hint.name)

    data = item_to_map(query, headers)
    return HttpResponse(json.dumps({"data": data, "headers": headers}),
                        content_type="application/json")


def ajax_give_hints():
    return HttpResponse(json.dumps({"hints": Item.objects.all().values_list('name', flat=True)},
                        content_type="application/json"))


def user_static_prefix(request):
    if False:
        return "mobile"
    return "desktop"


def confirm_order(c, u):
    if c == "true":
        pass
    else:
        if u and Order.objects.all().filter(customer_id=u.get_id()):
            user_orders = Order.objects.all().filter(customer_id=u.get_id())
            last_user_order = user_orders[user_orders.count()-1]
            last_user_order.delete()


def register_user(request, username, email, phone, password):
    if len(Customer.objects.all().filter(username=username)) > 0:
        return "user_invalid"
    if len(Customer.objects.all().filter(email=email)) > 0:
        return "email_invalid"
    if len(Customer.objects.all().filter(phone=phone)) > 0:
        return "phone_invalid"
    user = Customer.objects.create_user(username=username, email=email, phone=phone, password=password)
    login(request=request, user=user)
    return user


def get_custom_user(request):
    if request.user:
        user_id = request.user.id
        return Customer(user_id)

    elif request.session.get("temp-id"):
        user_id = request.session["temp-id"]
        user = TempUser.objects.all().filter(id=user_id)
        print("temp-id", user_id)
        if len(user) == 1:
            return user

    return None


def create_custom_user(request, name, email, phone):
    user = TempUser.objects.create(username=name, email=email, phone=phone)
    request.session["temp-id"] = user.id
    return user


def process_user_order(request):

    customer_name = request.GET.get('customer_name')
    item_amount = request.GET.get('item_amount')
    customer_phone = request.GET.get('customer_phone')
    customer_email = request.GET.get('customer_email')
    item_index = request.GET.get('item_id')

    user = get_custom_user(request)

    if user is None:
        user = create_custom_user(request, name=customer_name, phone=customer_phone, email=customer_email)

    item_name = Item.objects.all().filter(index=item_index)[0].name

    if item_index and customer_name and customer_phone and item_amount:

        created_order = Order.objects.create(customer_name=customer_name,
                                             customer_email=customer_email,
                                             customer_mobile=customer_phone,
                                             customer_id=user.get_id(),
                                             customer_is_logged_in=(isinstance(user, Customer)),

                                             item_id=item_index,
                                             item_amount=item_amount,
                                             item_name=item_name,
                                             )
    else:
        print("not all req fields", item_index, customer_name, customer_phone, item_amount)
        # format form response template with form state
        return HttpResponse(json.dumps({"success": False}), content_type="application/json")

    return HttpResponse(json.dumps({"success": True,
                                    "html": render_to_string('desktop/extendable/form_response.html', {"status": "success", "order": created_order})}),
                 content_type="application/json")


def process_user_data_request(request):

    username = None
    user_mail = None
    user_phone = None

    user_id = None
    is_logged_in = None

    if request.user:
        user_id = request.user.id
        is_logged_in = True
    elif request.session.get("temp-id"):
        user_id = request.user.id
        is_logged_in = False

    if user_id:
        if len(Order.objects.all().filter(customer_id=user_id, customer_is_logged_in=is_logged_in)) > 0:
            order = Order.objects.all().filter(customer_id=user_id)[len(Order.objects.all())-1]
            username = order.customer_name
            user_mail = order.customer_email
            user_phone = order.customer_mobile

        if request.user:
            username = request.user.username
            user_mail = request.user.email


    return HttpResponse(json.dumps(
        {"name": username,
         "email": user_mail,
         "phone": user_phone}),
        content_type="application/json")


def send_price_mail(receiver):
    msg = EmailMessage('Ежемесячная рассылка прайса', f'Здравствуйте, {receiver.username}!\nПрайс за {str(datetime.date.today())}.', 'RASTAprices@gmail.com', receiver.email)
    msg.content_subtype = "html"
    msg.attach_file('MainApp/pricelist/pricelist.xlsx')
    msg.send()


def send_confirmation_mail(user, code, next=""):

    msg = EmailMessage('Подтвердите свой электронный адрес',
                       f'<h1>Здравствуйте, {user.username}!</h1>'
                       f'<div>Для подтверждения своего адреса перейдите по ссылке ниже:</div>'
                       f'<a href="http://127.0.0.1:8000/accounts/confirm/?code={code}&action={next}">Подтверждение адреса</a>'
                       f'<div color="red"> Если вы не пытались подписаться на обновления с этого сайта, проигнорируйте это сообщение <div>',
                       'RASTAprices@gmail.com', [user.email])
    msg.content_subtype = "html"
    msg.send()


def set_user_code(user, code):
    USER_CODES[user] = code


def check_user_code(user, code):
    return USER_CODES.get(user) and USER_CODES.get(user)==code