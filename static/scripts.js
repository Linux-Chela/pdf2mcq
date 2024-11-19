// Open and close the modal
function openAskModal() {
    document.getElementById("askModal").style.display = "block";
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
                responseContainer.innerHTML = `<p><strong>Response:</strong> ${data.response}</p>`;
            } else {
                responseContainer.innerHTML = `<p>Error: ${data.error}</p>`;
            }
        })
        .catch(error => {
            responseContainer.innerHTML = `<p>Error: Something went wrong.</p>`;
        });
}
