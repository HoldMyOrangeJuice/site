
function open_image(index){
    console.log("open id ", "img"+index);
    console.log("show ", index+"close");
    document.getElementById("img"+index).style.display = "block";



}

document.addEventListener("click", close_image);
document.addEventListener("keydown", close_image);



function close_image(evt){
    console.log(evt.target);
    if(evt.target.type != "button")
    {
        $('.item_image').each(function(i, obj) {
        obj.style.display = "none";
    });
    }
}
