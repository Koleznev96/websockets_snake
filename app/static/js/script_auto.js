document.getElementById("button_auto").onclick = function() {
    var name = document.getElementById("inputLoginIn").value;
    var pass = document.getElementById("inputPasswordIn").value;
    
    if (name == "" || pass == "") {
        alert("Заполните все поля!");
    }
    else if (name != "" && pass != "") {
        window.location.href = '/';
    }

    document.getElementById("inputLoginIn").value = "";
    document.getElementById("inputPasswordIn").value = "";
}
document.getElementById("inputLoginIn").addEventListener('mouseenter', function(event) {
        event.target.setAttribute('autocomplete', 'off')
});