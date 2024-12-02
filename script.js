document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault();  
  
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
  
    if (!email || !password) {  
      alert("Details are required. Please enter both email and password.");
      return;  
    }
  
    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);
  
    if (emailValidation !== "Valid email." || passwordValidation !== "Valid password.") {
      alert(emailValidation || passwordValidation);  
    } else {
      window.location.href = "home.html"; 
    }
  });
  
  function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return "Invalid email format.";
    }
    if (existingEmails.includes(email)) {
      return "Account already exists.";
    }
    return "Valid email.";
  }
  
  function validatePassword(password) {
    const passwordRegex = /^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[@#$%^&+=]).{8,}$/;
    if (!passwordRegex.test(password)) {
      return "Password must have at least 8 characters, including uppercase, lowercase, number, and special character.";
    }
    return "Valid password.";
  }
  
