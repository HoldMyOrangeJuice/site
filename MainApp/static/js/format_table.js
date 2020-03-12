// function format_table(items, headers_json)
// {
//     if (items.length === 0 || headers_json.length === 0)
//             return;
//
//
//
//     let table_head = document.getElementById("js-table-head");
//     let table_body = document.getElementById("js-table-body");
//
//     rem_children("js-table-head");
//     rem_children("js-table-body");
//
//
//     let fields = Object.keys(headers_json);
//     let aliases = headers_json;
//
//     //determine mode:
//     let mode;
//
//     if (fields.includes("is_hidden"))
//         mode = "e";
//     else
//         mode = "v";
//     console.log('mode', mode, headers_json);
//
//     for (let field of fields)
//     {
//         let header = aliases[field];
//         let c = document.createElement("th");
//         c.innerText = header;
//         table_head.appendChild(c);
//         // set header
//     }
//
//     for (const [row_index, item, ]  of items.entries())
//     {
//
//         let e_row = document.createElement("tr");
//
//         for (const [col_index, field, ] of fields.entries())
//         {
//             setTimeout(function() {
//
//
//             let val = item[field];
//             let td;
//             switch (field)
//             {
//                 case "is_hidden":
//                     //add to table
//                     e = document.createElement("input");
//                     e.type = "checkbox";
//                     if (val)
//                         e.checked = "checked";
//                     td = document.createElement("td");
//                     td.appendChild(e);
//                     break;
//
//                 case "photo_link":
//                     //<img class="item_image" src="{{ item.photo_link }}" id="img{{ row_index }}" alt="{{ item.name }}">
//                     // add to document not to td
//                     e = document.createElement("img");
//                     e.src = val;
//                     e.hidden = true;
//                     e.id = `img${row_index}`;
//                     e.className = "item_image";
//                     td = document.createElement("td");
//                     td.appendChild(e);
//                     break;
//
//                 default:
//
//                     if (mode === "v")
//                     {
//                         if (field === "name")
//                         {
//                             let link = document.createElement("a");
//                             link.href = `/items?q=${item["index"]}`;
//                             link.innerText = val;
//                             td = document.createElement("td");
//                             td.appendChild(link);
//                         }
//                         else
//                         {
//                             td = document.createElement("td");
//                             td.innerText = val;
//                         }
//
//                     }
//                     else if (mode === "e")
//                     {
//                         e = document.createElement("input");
//                         e.value = val;
//                         e.setAttribute("data-id", item["id"]);
//                         e.setAttribute("data-field", field);
//                         td = document.createElement("td");
//                         td.appendChild(e);
//                     }
//
//             }
//             //add e to table
//             e_row.appendChild(td);
//         },1);
//         //add e_row to table
//         table_body.appendChild(e_row)
//             }
//     }
//
//
//
// }
//
