function rem_children(id)
{

    let dl = document.getElementById(id);

    let child = dl.lastElementChild;
    while (child)
    {
        dl.removeChild(child);
        child = dl.lastElementChild;
    }
}