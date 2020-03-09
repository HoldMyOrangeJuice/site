function format_table(items, headers_json)
{
    console.log(items);
    console.log(headers_json);

    let table_head = document.getElementById("js-table-head");
    let table_body = document.getElementById("js-table-body");

    rem_children("js-table-head");
    rem_children("js-table-body");


    let fields = Object.keys(items[0]);
    let aliases = headers_json;

    //determine mode:
    let mode;

    if (fields.includes("is_hidden"))
        mode = "e";
    else
        mode = "v";

    for (let field of fields)
    {
        let header = aliases[field]
        // set header
    }

    for (const [row_index, item, ]  of items.entries())
    {

        let e_row = document.createElement("tr");

        for (const [col_index, field, ] of fields.entries())
        {
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
                    //<img class="item_image" src="{{ item.photo_link }}" id="img{{ row_index }}" alt="{{ item.name }}">
                    // add to document not to td
                    e = document.createElement("img");
                    e.src = val;
                    e.hidden = true;
                    e.id = `img${row_index}`;
                    e.className = "item_image";
                    td = document.createElement("td");
                    td.appendChild(e);
                    break;

                default:

                    if (mode === "v")
                    {
                        td = document.createElement("td");
                        td.innerText = val;
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
        }
        //add e_row to table
        table_body.appendChild(e_row)
    }


}

// {% for row_index, item in table %}
//
//                 {% if item.photo_link %}
//
//                         <img class="item_image" src="{{ item.photo_link }}" id="img{{ row_index }}" alt="{{ item.name }}"> <!-- adding hidden image on page -->
//
//                 {% endif %}
//
//                     {% if mode == "edit" or not item.is_hidden %}
//                     <tr>
//                         {% for col_index, field in fields %}
//
//                             <td {% if field == "name" %}id="{{ item.name }}"{% endif %} class="{% if field == "photo_link" and mode == "edit" %} row_oriented {% endif %}{% if field == "name" %} name_column{% endif %}">
//                                 {% if mode == "edit" %}
//                                 <input
//                                     class="edit-table_input {% if field == "photo_link" %} photo_link_input{% endif %}"
//                                     data-id="{{item.id}}"
//                                     data-field="{{field}}"
//                                     value="{{ item|get_model_field:field }}"
//                                     type="{{ col_index|inp_type }}"
//
//                                     {% if item.is_hidden %}
//                                     checked="checked"
//                                     {% endif %}
//
//                                 />
//
//                                     {% if field == "photo_link" and item.photo_link %}
//
//                                         <button class="reveal_img photo_text" id="{{ row_index }}open" type="button" onclick="open_image({{ row_index }})">
//                                             Фото
//                                         </button>
//
//                                     {% endif %}
//
//
//
//                                 {% elif mode == "view" %}
//
//
//
//                                     {% if field != "photo_link"%}
//
//                                         {% if field == "name" %}
//
//                                             <a href="/items?q={{ item|get_model_field:"index" }}">{{ item|get_model_field:field }}</a>
//                                         {% else %}
//                                             {{ item|get_model_field:field }}
//                                         {% endif %}
//                                     {% else %}
//                                         {% if item.photo_link %}
//                                             <button id="{{ row_index }}open" type="button" class="reveal_img photo_text" onclick="open_image({{ row_index }})">
//                                                 Фото
//                                             </button>
//                                         {% endif %}
//                                     {% endif %}
//
//                                 {% endif %}
//
//
//                             </td>
//
//                         {% endfor %}
//                     </tr>
//                     {% endif %}
//
//
//
//
//                 {% endfor %}