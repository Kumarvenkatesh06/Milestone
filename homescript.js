// Get the popup container and its close button
const popup = document.querySelector(".popup-container"); // Adjusted to match your HTML structure
const closeButton = document.querySelector(".popup-close");

// Show the popup when the page loads or a specific event triggers
window.onload = () => {
    setTimeout(() => {
        popup.style.display = "flex"; // Assuming your CSS uses flexbox for centering
    }, 1000); // Delay popup display by 1 second
};

// Close the popup when clicking the close button
closeButton.addEventListener("click", () => {
    popup.style.display = "none"; // Hide the popup
});

// Optionally, close the popup when clicking outside of it
window.addEventListener("click", (event) => {
    if (event.target === popup) {
        popup.style.display = "none";
    }
});

const inputField = document.getElementById("username-input");
const submitButton = document.getElementById("submit-button");
const usernameDisplay = document.getElementById("username-display");

// Add event listener to the submit button
submitButton.addEventListener("click", () => {
    const username = inputField.value; // Get the value of the input field
    if (username.trim() !== "") {
        usernameDisplay.textContent = username; // Update the username in the greeting
    } else {
        usernameDisplay.textContent = "Guest"; // Fallback for empty input
    }
});


