function togglePasswordVisibility(passwordInputId, eyeIconId) {
    const passwordInput = document.getElementById(passwordInputId);
    const eyeIcon = document.getElementById(eyeIconId);
  
    if (passwordInput.type === "password") {
      // Gør adgangskoden synlig og skift til åbent øje uden streg
      passwordInput.type = "text";
      eyeIcon.innerHTML = `
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M12 4.5C7.58 4.5 4.16 7.11 2.47 10.5C4.16 13.89 7.58 16.5 12 16.5C16.42 16.5 19.84 13.89 21.53 10.5C19.84 7.11 16.42 4.5 12 4.5ZM12 12.5C10.76 12.5 9.75 11.49 9.75 10.25C9.75 9.01 10.76 8 12 8C13.24 8 14.25 9.01 14.25 10.25C14.25 11.49 13.24 12.5 12 12.5Z"
            fill="#1C274C"
          />
        </svg>
      `;
    } else {
      // Gør adgangskoden skjult og skift til øje med streg
      passwordInput.type = "password";
      eyeIcon.innerHTML = `
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M12 4.5C7.58 4.5 4.16 7.11 2.47 10.5C4.16 13.89 7.58 16.5 12 16.5C16.42 16.5 19.84 13.89 21.53 10.5C19.84 7.11 16.42 4.5 12 4.5ZM12 12.5C10.76 12.5 9.75 11.49 9.75 10.25C9.75 9.01 10.76 8 12 8C13.24 8 14.25 9.01 14.25 10.25C14.25 11.49 13.24 12.5 12 12.5Z"
            fill="#1C274C"
          />
          <path
            d="M3.293,20.707a1,1,0,0,1,0-1.414l16-16a1,1,0,1,1,1.414,1.414l-16,16A1,1,0,0,1,3.293,20.707Z"
            fill="#1C274C"
          />
        </svg>
      `;
    }
  }