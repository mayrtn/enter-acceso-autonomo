document.addEventListener("DOMContentLoaded", function () {

    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", function (e) {
            let valid = true;
            const requiredFields = form.querySelectorAll("input[required], select[required]");
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add("input-error");
                    valid = false;
                } else {
                    field.classList.remove("input-error");
                }
            });

            if (!valid) {
                e.preventDefault();
                alert("Por favor, completá todos los campos obligatorios.");
            }
        });
    });

    const toggles = document.querySelectorAll(".toggle-contraseña");
    toggles.forEach(toggle => {
        toggle.addEventListener("click", function () {
            const input = document.getElementById(this.dataset.target);
            if (input.type === "contraseña") {
                input.type = "text";
                this.innerHTML = '<i class="fa fa-eye-slash"></i>';
            } else {
                input.type = "contraseña";
                this.innerHTML = '<i class="fa fa-eye"></i>';
            }
        });
    });

    // Confirmaciones para botones con clase "confirmar"
    const confirmables = document.querySelectorAll(".confirmar");
    confirmables.forEach(button => {
        button.addEventListener("click", function (e) {
            const mensaje = this.dataset.confirm || "¿Estás seguro que querés continuar?";
            if (!confirm(mensaje)) {
                e.preventDefault();
            }
        });
    });

});

    function mostrarCamposPropietario() {
    const rol = document.getElementById("rol").value;
    const campos = document.getElementById("campos_propietario");
    campos.style.display = rol === "propietario" ? "block" : "none";
}