let max_pages;

function rem_children(id)
{

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


//
// function request_table(q)
// {
//
//     $.ajax({
//             type: "GET",
//             url: window.location.href,
//             data: { "q": q},
//             dataType: "json",
//             success:
//             function(data_json)
//             {
//                 console.log("s");
//                 console.log("success", data_json);
//                 let data = data_json["data"];
//                 let headers = data_json["headers"];
//
//                 if (data && headers)
//                     format_table(data, headers);
//
//                 // add autocomplete to search-box
//
//             }
//         })
// }


function pass_changes()
        {
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

    if (!document.getElementById("changes"))
    {

        let trgt = document.createElement("input");
        trgt.hidden = true;
        trgt.value = "{}";
        trgt.id = "changes";
        document.body.appendChild(trgt);
    }

    document.addEventListener("input", function (e) {
        console.log(e);
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
            console.log(e.target);
            input_el = e.target;
            changes = JSON.parse(document.getElementById("changes").value);
            let id = input_el.getAttribute("data-id");
            let field = input_el.getAttribute("data-field");
            if (input_el.type === "checkbox")
            {
                changes[`${id}|${field}`] = input_el.checked === true;
            }
            else
            {
                changes[`${id}|${field}`] = input_el.value;
            }

            console.log(changes);
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

// function reg_update_table_context() {
//     document.getElementById("search-box").addEventListener("input", function (e) {
//
//         let q = document.getElementById("search-box").value;
//
//
//         if (!document.getElementById("js-table-template"))
//         {
//             let table = document.createElement("table");
//             let thead = document.createElement("thead");
//             let tbody = document.createElement("tbody");
//             table.id = "js-table-template";
//             thead.id = "js-table-head";
//             tbody.id = "js-table-body";
//
//             table.appendChild(thead);
//             table.appendChild(tbody);
//             document.getElementsByTagName("body")[0].appendChild(table);
//
//         }
//         // request and draw table, hints
//         console.log("requesting upd");
//         request_table(q)
//     });
// }

function update_current_table_page(q, target_page, update_reason)
{
    let cur_page = get_page();
    if (cur_page === target_page && update_reason === "page-change")
        return;

    set_page(target_page);
    console.log("setting target page", target_page);

    $.ajax({
        type: "GET",
        url: document.location.href,
        data: {"q":q, "p":target_page},
        success: function (response)
        {
            max_pages = response['max-pages'];
            format_table(response["query"], response["headers"]);
            console.log("got response", response);
        }
    });






}

function format_table(items, headers_json)
{

    if (items.length === 0 || headers_json.length === 0)
    {
        set_page(0);
        return;
    }

    let avg_col_w = 130;

    let table_head = document.getElementById("js-table-head");
    let table_body = document.getElementById("js-table-body");

    rem_children("js-table-head");
    rem_children("js-table-body");
    rem_children("static-thead");


    let fields = Object.keys(headers_json);


    let w = $(document).width();

    console.log("screen", w);
    console.log("calc", headers_json, w);
    let cols_to_miss = Math.ceil (((Object.keys(headers_json).length * avg_col_w) - w )/ avg_col_w);
    let cropped_fields;
    console.log("skip", cols_to_miss);
    if (cols_to_miss >0)
        cropped_fields = fields.slice(0, Object.keys(headers_json).length - cols_to_miss);
    else
        cropped_fields = fields;

    console.log(fields);
    let aliases = headers_json;

    //determine mode:
    let mode;

    if (fields.includes("is_hidden"))
        mode = "e";
    else
        mode = "v";

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



        // <table id="view-header" class="nav_header" hidden="hidden">
        // <thead class="static-thead">
        //
        //     {% for header in headers %}
        //
        //         <th class="th-inner th-static">
        //             {{ header }}
        //         </th>
    }

    for (const [row_index, item, ]  of items.entries())
    {

        let e_row = document.createElement("tr");

        for (const [col_index, field, ] of cropped_fields.entries())
        {
            setTimeout(function() {


            let val = item[field];
            let td;

            switch (field)
            {
                case "is_hidden":
                    //add to table
                    e = document.createElement("input");
                    e.type = "checkbox";
                    if (val)
                        e.checked = "checked";
                    td = document.createElement("td");
                    td.appendChild(e);
                    break;

                case "photo_link":
                    if (mode === "e")
                    {
                        e = document.createElement("input");
                        e.value = val;
                        e.setAttribute("data-id", item["id"]);
                        e.setAttribute("data-field", field);
                        td = document.createElement("td");
                        td.appendChild(e);
                    }
                    else if (val)
                    {
                        e = document.createElement("img");
                        e.src = val;
                        e.id = `img${row_index}`;
                        e.className = "item_image";
                        // e.style.display = "none";
                        document.getElementsByTagName("body")[0].appendChild(e);
                        console.log("id", document.getElementById(e.id));


                        let open_img = document.createElement("a");
                        open_img.innerText = "фото";
                        open_img.id = (e.id).replace("img", "open");
                        open_img.onclick = function(e)
                        {
                          open_image(e.target.id.replace("open", ""));
                        };

                        td = document.createElement("td");
                        td.appendChild(open_img);
                    }
                    else
                    {
                        td = document.createElement("td");
                        td.innerText = "-"
                    }
                    //<img class="item_image" src="{{ item.photo_link }}" id="img{{ row_index }}" alt="{{ item.name }}">
                    // add to document not to td
                    break;

                default:

                    if (mode === "v")
                    {
                        if (field === "name")
                        {
                            let link = document.createElement("a");
                            link.href = `/items?q=${item["index"]}`;
                            link.innerText = val;
                            td = document.createElement("td");
                            td.appendChild(link);
                        }
                        else
                        {
                            td = document.createElement("td");
                            if (val.length > 20 && val.length - 20 > 3)
                            {
                                td.innerText = val.substring(0, 20) + "...";
                                td.title = val;
                            }
                            else
                                td.innerText = val;
                        }

                    }
                    else if (mode === "e")
                    {
                        e = document.createElement("input");
                        e.value = val;
                        e.setAttribute("data-id", item["id"]);
                        e.setAttribute("data-field", field);
                        td = document.createElement("td");
                        td.appendChild(e);
                    }

            }
            //add e to table
            e_row.appendChild(td);
        },1);
        //add e_row to table
        table_body.appendChild(e_row)
            }
    }

}

function get_page()
{
    console.log(document.getElementById("page-index"));
    if (!document.getElementById("page-index").value)
            return "no_page_found";

    let page = parseInt(document.getElementById("page-index").value);
    if (!isNaN(page))
        return page;
    return 0;
}

function set_page(i)
{
    console.log("setting", i);
        let  indexes = document.getElementsByClassName("cur-page-index");
        for (let item of indexes) {
            item.innerText = i;
        }
    document.getElementById("page-index").value = parseInt(i);
}

function render_page(i)
{
    let page = get_page();


    page = page + i;
    console.log("tryna render", page);
    if (page >= 0 && page < max_pages)
    {
        // normal
        console.log("OK");
    }
    else if (page < 0)
    {
        console.log("page_negative");
        if (max_pages)
        {
            page = (max_pages-1);
        }
        else
            page =(0);

    }
    else if(page >= max_pages)
    {
        console.log("page_don_exist");
        page = (0);
    }


    let q = document.getElementById("search-box").value;
    update_current_table_page(q, page, "page-change");
}


function search_in_price_from_another_loc(q)
{
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

function mobile_page()
{
    let h = window.screen.height;
    let w = window.screen.width;
    if (window.mobilecheck)
    {
        alert("mobile user");
        console.log("mobile user");
    }

    else
        return;

    let style = document.createElement("style");
    style.innerText="html{font-size: 1.6rem } " +
        ".mobile{display: flex;\n" +
        "flex-direction: column;}";
    document.getElementsByTagName("body")[0].appendChild(style);

}

