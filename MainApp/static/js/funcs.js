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


    let table_head = document.getElementById("js-table-head");
    let table_body = document.getElementById("js-table-body");

    rem_children("js-table-head");
    rem_children("js-table-body");


    let fields = Object.keys(headers_json);
    console.log(fields);
    let aliases = headers_json;

    //determine mode:
    let mode;

    if (fields.includes("is_hidden"))
        mode = "e";
    else
        mode = "v";

    for (let field of fields)
    {
        let header = aliases[field];
        let c = document.createElement("th");
        c.innerText = header;
        table_head.appendChild(c);
        // set header
    }

    for (const [row_index, item, ]  of items.entries())
    {

        let e_row = document.createElement("tr");

        for (const [col_index, field, ] of fields.entries())
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