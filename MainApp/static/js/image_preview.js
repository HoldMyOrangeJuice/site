
function open_image(index){
    console.log("open id ", "img"+index);
    console.log("show ", index+"close");
    document.getElementById("img"+index).style.display = "block";
    img_w = 640; //document.getElementById("img"+index).offsetWidth;
    img_h = 480; //document.getElementById("img"+index).offsetHeight;
    wv_w = document.documentElement.clientWidth;
    wv_h = document.documentElement.clientHeight;
    console.log(img_w, img_h, "image");
    console.log(wv_w, wv_h, "window");
    console.log("pad left", (wv_w - img_w)/2 +" px");
    console.log("pad right", (wv_w - img_w)/2 +" px");
    console.log("pad top", (wv_w - img_w)/2 +" px");
    console.log("pad bot",(wv_w - img_w)/2 +" px");

    document.getElementById("img"+index).style.paddingLeft =  (wv_w - img_w)/2 +"px";
    document.getElementById("img"+index).style.paddingRight = (wv_w - img_w)/2 +"px";
    document.getElementById("img"+index).style.paddingTop = (wv_h - img_h)/2 +"px";
    document.getElementById("img"+index).style.paddingBottom = (wv_h - img_h)/2 +"px";


    window.onresize = function(event) {
    wv_w = document.documentElement.clientWidth;
    wv_h = document.documentElement.clientHeight;
    document.getElementById("img"+index).style.paddingLeft =  (wv_w - img_w)/2 +"px";
    document.getElementById("img"+index).style.paddingRight = (wv_w - img_w)/2 +"px";
    document.getElementById("img"+index).style.paddingTop = (wv_h - img_h)/2 +"px";
    document.getElementById("img"+index).style.paddingBottom = (wv_h - img_h)/2 +"px";
    };
    //document.getElementById("img"+index).style.paddingBottom = "100px";

    console.log(document.getElementById("img"+index))



}

document.addEventListener("click", close_image);
document.addEventListener("keydown", close_image);



function close_image(evt){
    if(evt.target.type != "button" || evt.key)
    {
        $('.item_image').each(function(i, obj) {
        obj.style.display = "none";
    });
    }
}
