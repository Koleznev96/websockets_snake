document.getElementById("button_re").onclick = function() {
    var name = document.getElementById("inputLogin").value;
    var pass = document.getElementById("inputPassword").value;
    var confirm_pass = document.getElementById("inputConfirmPassword").value;
    
    if (name == "" || pass == "" || confirm_pass == "") {
        alert("Заполните все поля!");
    }
    else if (pass != confirm_pass) {
        alert("Пароли не совпадают!");
    }
    if (name != "" && pass != "" && confirm_pass != "" && pass == confirm_pass) {
        window.location.href = '/';
    }

    document.getElementById("inputLogin").value = "";
    document.getElementById("inputPassword").value = "";
    document.getElementById("inputConfirmPassword").value = "";
	
}

document.getElementById('inputLogin').addEventListener('mouseenter', function(event) {
        event.target.setAttribute('autocomplete', 'off')
});