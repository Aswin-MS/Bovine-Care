document.addEventListener("DOMContentLoaded", function () {
    emailjs.init("FVqfFAVH54b21ToNZ"); // Your Public Key

    document.getElementById("contact-form").addEventListener("submit", function (event) {
        event.preventDefault();

        emailjs.sendForm("service_i9o12hb", "template_jst5wiv", this)
            .then(function () {
                document.getElementById("status-message").innerHTML = "Message sent successfully!";
                document.getElementById("contact-form").reset();
            }, function (error) {
                document.getElementById("status-message").innerHTML = "Failed to send message. Try again later.";
                console.error("EmailJS Error:", error);
            });
    });
});



