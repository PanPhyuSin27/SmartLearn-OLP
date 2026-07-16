document.addEventListener("DOMContentLoaded", () => {
    console.log("SmartLearn Homepage Loaded");
});



// home.html ___________________

console.log("SmartLearn Home Page Loaded 🚀");

// simple interaction
// document.querySelector(".btn-primary").addEventListener("click", () => {
//     alert("Redirecting to Dashboard...");
// });

function goToSignup() {
    window.location.href = "register.html";
}

function goToLogin() {
    window.location.href = "login.html";
}

function goToDashboard() {
    window.location.href = "dashboard.html";
}

function goToHome() {
    window.location.href = "home.html";
}


// login.html
//function login(e) {
//            e.preventDefault();
//            alert("Login UI only");
//            window.location.href = "home.html";
//        }



// register.html
        function register(e) {
            e.preventDefault();
            alert("Register UI only");
            window.location.href = "login.html";
        }


