// Open and close the modal
function openAskModal() {
    document.getElementById("askModal").style.display = "block";
    document.getElementById("responseContainer").innerHTML = ""; // Clear previous responses
}

function closeAskModal() {
    document.getElementById("askModal").style.display = "none";
}

// Submit user prompt
function submitPrompt() {
    const prompt = document.getElementById("userPrompt").value;
    const responseContainer = document.getElementById("responseContainer");

    if (!prompt.trim()) {
        alert("Please enter a prompt.");
        return;
    }

    // Display "Generating..." with animation
    responseContainer.innerHTML = `
        <p class="hacker-text typing-animation">Generating...</p>
    `;

    fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt })
    })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                responseContainer.innerHTML = `<p class="hacker-text"><strong>Response:</strong> ${data.response}</p>`;
            } else {
                responseContainer.innerHTML = `<p class="hacker-text">Error: ${data.error}</p>`;
            }
        })
        .catch(error => {
            responseContainer.innerHTML = `<p class="hacker-text">Error: Something went wrong.</p>`;
        });
}
