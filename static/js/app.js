document.addEventListener("DOMContentLoaded", function() {
    // Функция для валидации формы
    function validateForm(event) {
        // Получаем значения всех полей
        const shippingName = document.getElementById("shipping_name").value.trim();
        const driver = document.getElementById("driver").value.trim();
        const vehicle = document.getElementById("vehicle").value.trim();
        const startingPoint = document.getElementById("starting_point").value.trim();
        const destinationPoint = document.getElementById("destination_point").value.trim();

        // Проверка, если хотя бы одно поле пустое
        if (!shippingName || !driver || !vehicle || !startingPoint || !destinationPoint) {
            // Отображаем сообщение об ошибке
            document.getElementById("error-message").style.display = "block";

            // Останавливаем отправку формы
            event.preventDefault();
        } else {
            // Скрываем сообщение об ошибке, если все поля заполнены
            document.getElementById("error-message").style.display = "none";
        }
    }

    // Добавляем обработчик на событие отправки формы
    const form = document.getElementById("shippingForm");
    if (form) {
        form.addEventListener("submit", validateForm);
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const loginInput = document.getElementById("login");
    const errorMessage = document.getElementById("login-error-message");

    // Событие потери фокуса на поле логина
    loginInput.addEventListener("blur", function () {
        const login = loginInput.value.trim();

        if (login) {
            // Асинхронный запрос для проверки уникальности логина
            fetch(`/check_login/${login}`)
                .then(response => response.json())
                .then(data => {
                    if (data.exists) {
                        // Если логин уже занят, показываем ошибку
                        errorMessage.style.display = "block";
                    } else {
                        // Если логин свободен, скрываем ошибку
                        errorMessage.style.display = "none";
                    }
                })
                .catch(error => {
                    console.error('Ошибка при проверке логина:', error);
                });
        }
    });
});
