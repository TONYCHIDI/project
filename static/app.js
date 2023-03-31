const openTab = (evt) => {
    let tablinks = document.getElementsByClassName("nav-link");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" nav-btn", "");
    }
    evt.currentTarget.className += " nav-btn";
}
