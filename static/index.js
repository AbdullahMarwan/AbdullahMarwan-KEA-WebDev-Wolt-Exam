document.addEventListener("DOMContentLoaded", () => {
    const loginBtn = document.getElementById("login-btn");
    const signupBtn = document.getElementById("signup-btn");
    const loginBox = document.getElementById("login-box");
    const signupBox = document.getElementById("signup-box");

    const loginLink = document.getElementById("login-link");
    const signupLink = document.getElementById("signup-link");

    // Funktion til at vise og skjule bokse
    function toggleBoxes(showBox, hideBox) {
        showBox.style.display = "block";
        hideBox.style.display = "none";
    }

    // Vis login-boksen
    loginBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleBoxes(loginBox, signupBox);
    });

    // Vis signup-boksen
    signupBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleBoxes(signupBox, loginBox);
    });

    // Login-link åbner login-boksen
    loginLink.addEventListener("click", (e) => {
        e.preventDefault();
        toggleBoxes(loginBox, signupBox);
    });

    // Signup-link åbner signup-boksen
    signupLink.addEventListener("click", (e) => {
        e.preventDefault();
        toggleBoxes(signupBox, loginBox);
    });

    // Luk bokse, hvis man klikker udenfor dem
    document.addEventListener("click", (e) => {
        if (!loginBox.contains(e.target) && !loginBtn.contains(e.target) && !loginLink.contains(e.target)) {
            loginBox.style.display = "none";
        }
        if (!signupBox.contains(e.target) && !signupBtn.contains(e.target) && !signupLink.contains(e.target)) {
            signupBox.style.display = "none";
        }
    });

    // Stop propagation indenfor boksene
    loginBox.addEventListener("click", (e) => e.stopPropagation());
    signupBox.addEventListener("click", (e) => e.stopPropagation());
});