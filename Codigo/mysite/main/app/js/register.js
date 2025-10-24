document.addEventListener("DOMContentLoaded", function () {
    const password1 = document.getElementById("password1");
    const password2 = document.getElementById("password2");
    const form = document.querySelector("form");

    // Crear un elemento dinámico para mostrar mensajes
    const msg = document.createElement("small");
    msg.style.display = "block";
    msg.style.marginTop = "5px";
    msg.style.fontWeight = "600";
    msg.style.fontSize = "14px";
    password2.parentNode.appendChild(msg);

    // Validar en tiempo real si coinciden las contraseñas
    password2.addEventListener("input", () => {
        if (password1.value && password2.value) {
            if (password1.value === password2.value) {
                msg.textContent = "✅ Las contraseñas coinciden";
                msg.style.color = "green";
                password2.style.borderColor = "green";
            } else {
                msg.textContent = "❌ Las contraseñas no coinciden";
                msg.style.color = "red";
                password2.style.borderColor = "red";
            }
        } else {
            msg.textContent = "";
            password2.style.borderColor = "#003a70";
        }
    });

    // Prevenir envío si las contraseñas no coinciden
    form.addEventListener("submit", (e) => {
        if (password1.value !== password2.value) {
            e.preventDefault();
            alert("Las contraseñas no coinciden. Por favor, verifica.");
            password2.focus();
        }
    });
});