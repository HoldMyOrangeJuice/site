let max_pages;
let items;
let headers;

// order
let ordered_id = null
let customer_data = null
let form_data = null



function rem_children(id)
{
    console.log("rem_children")

    let dl = document.getElementById(id);

    if (!dl)
        return;

    let child = dl.lastElementChild;
    while (child)
    {
        dl.removeChild(child);
        child = dl.lastElementChild;
    }
}

function pass_changes()
    {
    console.log("pass_changes")

        var csrftoken = getCookie('csrftoken');

        $.ajaxSetup({
        beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        });

        $.ajax({
        type: "POST",
        url: "/adm/",
        data: { "changes": document.getElementById("changes").value}
        })
    }

function reg_change_listener() {
console.log("reg_change_listener")


    if (!document.getElementById("changes"))
    {
        let trgt = document.createElement("input");
        trgt.hidden = true;
        trgt.value = "{}";
        trgt.id = "changes";
        document.body.appendChild(trgt);
    }

    document.addEventListener("input", function (e)
    {
        if (e.target.className !== "change-entry")
            return;
            if(e.target.getAttribute("value") !== e.target.value && e.target.getAttribute("data-field"))
            {
                e.target.style.color = "green"
            }
            else
            {
                e.target.style.color = "black"
            }
            if(e.target.value==="" && e.target.getAttribute("data-field") === "name")
            {
                e.target.setAttribute("placeholder", `${e.target.getAttribute("value")} Будет удален`)
            }

            input_el = e.target;
            changes = JSON.parse(document.getElementById("changes").value);
            let id = input_el.getAttribute("data-id");
            let field = input_el.getAttribute("data-field");

            if (!id || !field)return;

            if (input_el.type === "checkbox")
            {
                changes[`${id}|${field}`] = input_el.checked === true;
            }
            else
            {
                changes[`${id}|${field}`] = input_el.value;
            }


            document.getElementById("changes").value = JSON.stringify(changes)
    })
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function update_current_table_page(q, target_page, update_reason)
{
console.log("update_current_table_page")
    let cur_page = get_page();
    if (cur_page === target_page && update_reason === "page-change")
        return;

    set_page(target_page);

    $.ajax({
        type: "GET",
        url: document.location.href,
        data: {"q":q, "p":target_page},
        success: function (response)
        {
            max_pages = response['max-pages'];
            items = response["query"]
            headers = response["headers"];
            entry_count = response['entries']
            format_table(items, headers, entry_count, q);
        }
    });

}


function format_table(items, headers_json, query_resp_entries, q)
{
    console.log("format_table")
    let ignore_fields = ["index"];

    let count = document.getElementById("entry-count");
    let count_text = "";

    if ((query_resp_entries-1)%10===0)
        count_text = `Найден ${query_resp_entries} результат по запросу ${q}`;
    else if (query_resp_entries%10>1 && query_resp_entries%10<5)
        count_text = `Найдено ${query_resp_entries} результата по запросу ${q}`;
    else
        count_text = `Найдено ${query_resp_entries} результатов по запросу ${q}`;

    count.innerText = count_text;

    if (Object.keys(items).length === 0 || headers_json.length === 0)
    {
        set_page(0);
        return;
    }



    let table_head = document.getElementById("js-table-head");
    let table_body = document.getElementById("js-table-body");


    let avg_col_w = window.mobilecheck()?160:110;//table_head.offsetWidth / Object.keys(headers_json).length;

    rem_children("js-table-head");
    rem_children("js-table-body");
    rem_children("static-thead");


    let fields = Object.keys(headers_json);

    let mode;

    if (fields.includes("is_hidden"))
        mode = "e";
    else
        mode = "v";

    if (mode === "v")
    {
        fields.push("order");
        fields.splice(fields.indexOf("index"),1);

    }

    let w = $(document).width();


    let cols_to_miss = Math.ceil (((Object.keys(headers_json).length * avg_col_w) - w )/ avg_col_w);
    let cropped_fields;

    if (cols_to_miss > 0 && !window.location.href.includes("adm") )
    {
        cropped_fields = fields.slice(0, Object.keys(headers_json).length - cols_to_miss);
    }

    else
    {
        cropped_fields = fields;
    }

    headers_json["order"]="Заказать";
    let aliases = headers_json;

    //determine mode:
    for (let field of cropped_fields)
    {
        let header = aliases[field];

        let c = document.createElement("th");
        c.innerText = header;
        table_head.appendChild(c);
        // set header

        let table_static = document.getElementById("view-header");
        table_static.hidden = true;
        let thead_static = document.getElementById("static-thead");
        let th = document.createElement("th");
        th.innerText = aliases[field];
        th.className = "th-inner th-static";
        thead_static.appendChild(th);

    }

    for (const [row_index, item, ]  of Object.values(items).entries())
    {
        let e_row = document.createElement("tr");
        for (const [col_index, field, ] of cropped_fields.entries()) {
            setTimeout(function () {

                let val = item[field];
                let td;
                switch (field) {

                    case "index":
                        break;

                    case "order":
                        let make_order = document.createElement("td");
                        let button = document.createElement("button");
                        button.innerText = "Заказать";
                        let cur_item_row_id = item["index"];
                        button.type = "button";
                        $(button).addClass("button");
                        // prevents onclick disappearing after form sent, .onclick=()=>{} does not work properly

                        button.setAttribute("onclick", `open_order_window(${cur_item_row_id})`);

                        make_order.appendChild(button);

                        if (mode === "v")
                            td = make_order;
                        break;

                    case "is_hidden":
                        //add to table
                        e = document.createElement("input");
                        e.className = "change-entry";
                        e.setAttribute("data-id", item["id"]);
                        e.setAttribute("data-field", field);
                        e.type = "checkbox";
                        if (val)
                            e.checked = "checked";
                        td = document.createElement("td");
                        td.appendChild(e);
                        break;

                    case "photo_link":
                        if (mode === "e") {
                            e = document.createElement("input");
                            e.className = "change-entry";
                            e.value = val;
                            e.setAttribute("data-id", item["id"]);
                            e.setAttribute("data-field", field);
                            td = document.createElement("td");
                            td.appendChild(e);
                        } else if (val) {
                            e = document.createElement("img");
                            e.src = val;
                            e.id = `img${row_index}`;
                            e.className = "item_image";
                            // e.style.display = "none";
                            document.getElementsByTagName("body")[0].appendChild(e);

                            let open_img = document.createElement("a");
                            open_img.innerText = "фото";
                            open_img.className = "item_link";
                            open_img.id = row_index + "open";
                            open_img.setAttribute("onclick",`open_image(${row_index})`);
                            console.log(open_img);
                            td = document.createElement("td");
                            td.appendChild(open_img);
                        } else {
                            td = document.createElement("td");
                            td.innerText = "-"
                        }
                        //<img class="item_image" src="{{ item.photo_link }}" id="img{{ row_index }}" alt="{{ item.name }}">
                        // add to document not to td
                        break;

                    default:

                        if (mode === "v") {
                            if (field === "name") {
                                let link = document.createElement("a");
                                link.href = `/items?q=${item["index"]}`;
                                link.className = "item_link";
                                link.innerText = val;
                                td = document.createElement("td");
                                td.appendChild(link);
                            } else {
                                let units = "";
                                if (field === "price")
                                    units = " грн";
                                else if (field === "amount")
                                    units = " шт";

                                td = document.createElement("td");
                                if (val && val.length > 20 && val.length - 20 > 3) {
                                    td.innerText = val.substring(0, 20) + "...";
                                    td.title = val + units;
                                } else if (val)
                                    td.innerText = val + units;
                            }

                        } else if (mode === "e") {
                            e = document.createElement("input");
                            e.className = "change-entry";
                            e.value = val;
                            e.setAttribute("data-id", item["id"]);
                            e.setAttribute("data-field", field);
                            td = document.createElement("td");
                            td.appendChild(e);
                        }

                }
                e_row.appendChild(td);
            }, 1);
        }
        //add e_row to table
        table_body.appendChild(e_row);
    }
}



function get_page()
{
console.log("get_page")
    if (!document.getElementById("page-index").value)
            return "no_page_found";

    let page = parseInt(document.getElementById("page-index").value);
    if (!isNaN(page))
        return page;
    return 0;
}

function set_page(i)
{
console.log("set_page")
    let  indexes = document.getElementsByClassName("cur-page-index");
    for (let item of indexes)
    {
        item.innerText = i;
    }
    document.getElementById("page-index").value = parseInt(i);
}

function render_page(i)
{
console.log("render_page")
    let page = get_page();
    page = page + i;

    if (page >= 0 && page < max_pages)
    {
        // normal
    }
    else if (page < 0)
    {

        if (max_pages)
        {
            page = (max_pages-1);
        }
        else
            page =(0);

    }
    else if(page >= max_pages)
    {

        page = (0);
    }

    let q = document.getElementById("search-box").value;
    update_current_table_page(q, page, "page-change");
}


function search_in_price_from_another_loc(q)
{
console.log("search_in_price_from_another_loc")

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", document.location.href, false );
    xmlHttp.send( {"q":q, "p":0} );
    return xmlHttp.responseText;
}

window.mobilecheck = function() {
  var check = false;
  (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);
  return check;
};


function open_order_window(id, retry)
{
console.log("open_order_window")

    ordered_id = id;

    let item_price = items[id]["amount"];
    let item_name = items[id]["name"];
    let item_max_amount = items[id]["amount"];

    form = document.getElementById("order-form-hidden");
    form.classList.remove("hidden");
    console.log("overlay opened")

    let item_label = document.getElementById("form_item_label");
    item_label.innerText = item_name;

    let amount_input = document.getElementById("form_amount_input");
    amount_input.value = 1;
    amount_input.max = item_max_amount;

    amount_input.addEventListener("input", ()=>
    {
    // calculate price on amount input update
    let total = item_price * amount_input.value;
    $("#form-total-price").text(`total price: ${total} uah`);
    });
    form.dispatchEvent(new Event("input"));


    // format form with user's data
    if (!retry)
        request_user_info(fill_form_with_user_data);
}

function request_user_info(callback)
{
console.log("request_user_info")
    $.ajax({
        type: "GET",
        url: location.protocol + '//' + location.host + location.pathname,
        data: {"give_me_user_data":"yes"},
        success:  (user_data) =>
        {
            callback(user_data)
        }
    });
}


function fill_form_with_user_data(data)
{
console.log("fill_form_with_user_data")
    if (!data)return
    $("#name").val(data["name"]);
    $("#phone").val(data["phone"]);
    $("#email").val(data["email"]);
}

function submit_order_form()
{
console.log("submit_order_form")
    let form_data = process_order_form();
    customer_data = form_data

    $.ajax({
        type: "GET",
        url: location.protocol + '//' + location.host + location.pathname,
        data:
            {
            "action": "order",
            "item_name": form_data["item_name"],
            "customer_name": form_data["customer_name"],
            "item_amount": form_data["item_amount"],
            "customer_phone": form_data["customer_phone"],
            "customer_email": form_data["customer_email"],
            "item_id": form_data["item_id"]
            },
        success:(response) =>
        {
            //alert(response_text);
            if (response["success"] == false)
            {
                open_order_window(ordered_id, true)
                set_form_data(customer_data)
            }
            else
            {
                document.getElementsByTagName("body")[0].innerHTML += response.html;
            }
        }
    });
}

function process_order_form()
{
    let item_input = document.getElementById("form_item_input");
    let amount_input = document.getElementById("form_amount_input");
    let name_input = document.getElementById("name");
    let phone_input = document.getElementById("phone");
    let email_input = document.getElementById("email");

    return {
            "customer_name": name_input.value,
            "item_amount": amount_input.value,
            "customer_phone": phone_input.value,
            "customer_email": email_input.value,
            "item_id": ordered_id
            }
}

function set_form_data(form_data)
{
    if (!form_data)return
    document.getElementById("form_amount_input").value = form_data.item_amount;

    document.getElementById("name").value = form_data.customer_name;
    document.getElementById("phone").value = form_data.customer_phone;
    document.getElementById("email").value = form_data.customer_email;


}

function close_overlay()
{
$(".overlay").addClass("hidden")
console.log("overlay closed")
}

function remove_overlay(id){($(`#${id}`)).remove()}

function send_order_status(confirmed)
{
    let order_id = $("#ordered-item-id").val();
    console.log(confirmed);
    $.ajax({
        type: "GET",
        url: location.protocol + '//' + location.host + location.pathname,
        data: {"confirmed": confirmed?"true":"false", "orderID": order_id},
        success:  () =>
        {
            if (confirmed)
                alert("successfully confirmed");
            else
                alert("successfully canceled");
        }

    });
}

function seen_order(elem, order_id)
{
    $( elem ).parent().removeClass("new");
    $( elem ).parent().addClass("seen");

    $.ajax({
        type: "GET",
        url: location.protocol + '//' + location.host + location.pathname,
        data: {"seen_order": "yes", "order_id": order_id},
        // success:  (order_data) =>
        // {
        //
        // }
    });
}

function delete_order(elem, order_id)
{

     $.ajax({
        type: "GET",
        url: location.protocol + '//' + location.host + location.pathname,
        data: {"delete_order": "yes", "order_id": order_id},
        // success:  (order_data) =>
        // {
        //
        // }
    });

}

function submit_form(form_id)
{
    var url_string = window.location.href;
    var url = new URL(url_string);
    let next = url.searchParams.get("next");

    console.log( $("#" + form_id ).serialize()+ "&next=" + next)
    $.ajax({
      type: 'POST',
      url: location.protocol + '//' + location.host + location.pathname,
      data: $("#" + form_id ).serialize() + "&next=" + next,
      success: function(response)
      {

            console.log(response)
            $("#status")[0].innerText = response.response
            if (response.redirect){location.pathname = response.redirect}
      },
    });

}

function sub_to_mailing(form_id)
{
  $.ajax({
      type: 'GET',
      url: location.protocol + '//' + location.host + location.pathname,
      data: $("#" + form_id ).serialize(),
      success: function(response)
      {
            console.log(response)
            inform(response.response)
            if (response.redirect){location.pathname = response.redirect}
      },
    });
}

function inform(message)
{
    alert(message)
}