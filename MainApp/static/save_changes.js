document.addEventListener('input', function (evt) {
    add_change(this);
});
let changes = {};

function add_change(e)
{
    let form_elem = document.getElementById("changes");
    let elem = document.activeElement;
    let elem_name = elem.getAttribute("data-key");
    if (elem.type == "text")
    {
        console.log(elem_name);
        changes[elem_name] = elem.value;
        console.log("changes ", changes);
        console.log("evt", elem);
    }
    if (elem.type == "checkbox")
    {
        if (elem.checked)
        {
            console.log(elem_name);
            changes[elem_name] = "false";
            console.log("changes ", changes);
            console.log("evt", elem);
        } else
        {
            console.log(elem_name);
            changes[elem_name] = "true";
            console.log("changes ", changes);
            console.log("evt", elem);
        }

    }

    form_elem.value = JSON.stringify(changes)
}

