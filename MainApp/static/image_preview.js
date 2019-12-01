
function open_image(index){
    console.log("open id ", "img"+index);
    console.log("show ", index+"close");
    document.getElementById("img"+index).hidden = false;

    document.getElementById(index+"open").hidden = true;
    document.getElementById(index+"close").hidden = false;
}
function close_image(index){
    console.log("close id ", "img"+index);
    document.getElementById("img"+index).hidden = true;

    document.getElementById(index+"open").hidden = false;
    document.getElementById(index+"close").hidden = true;
}
