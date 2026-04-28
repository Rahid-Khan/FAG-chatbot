const input = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");
const chatWindow = document.getElementById("chatWindow");
const statusText = document.getElementById("statusText");
const confidenceBadge = document.getElementById("confidenceBadge");
const clearBtn = document.getElementById("clearBtn");
const quickQuestions = document.querySelectorAll(".quick-question");
const welcomeTime = document.getElementById("welcomeTime");
const STORAGE_KEY = "faq_chatbot_messages";

function formatTime() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function appendMessage(text, role, timeLabel = formatTime()) {
    const row = document.createElement("div");
    row.className = `message-row ${role}`;

    const bubble = document.createElement("article");
    bubble.className = `message ${role}`;

    const textNode = document.createElement("p");
    textNode.textContent = text;

    const timeNode = document.createElement("span");
    timeNode.className = "message-time";
    timeNode.textContent = timeLabel;

    bubble.appendChild(textNode);
    bubble.appendChild(timeNode);
    row.appendChild(bubble);
    chatWindow.appendChild(row);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return row;
}

function setConfidenceBadge(confidence, matched) {
    confidenceBadge.className = "confidence-badge";
    if (!confidence) {
        confidenceBadge.classList.add("confidence-neutral");
        confidenceBadge.textContent = "Waiting for a question";
        return;
    }

    confidenceBadge.classList.add(`confidence-${confidence}`);
    confidenceBadge.textContent = matched
        ? `Confidence: ${confidence}`
        : `Fallback used (${confidence})`;
}

function saveConversation() {
    localStorage.setItem("faq_chatbot_messages", chatWindow.innerHTML);
}

function restoreConversation() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        chatWindow.innerHTML = saved;
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
}

async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, "user");
    input.value = "";
    input.focus();

    sendBtn.disabled = true;
    statusText.textContent = "Assistant is typing...";
    const loadingNode = appendMessage("Thinking...", "bot", "now");

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });

        const data = await response.json();
        loadingNode.remove();

        if (!response.ok) {
            appendMessage(data.response || "Something went wrong. Please try again.", "bot");
            statusText.textContent = "Request failed";
            setConfidenceBadge(null, false);
            saveConversation();
            return;
        }

        appendMessage(data.response, "bot");
        statusText.textContent = "Ready";
        setConfidenceBadge(data.meta?.confidence, data.meta?.matched);
        saveConversation();
    } catch (error) {
        loadingNode.remove();
        appendMessage("Network error. Please check if the server is running.", "bot");
        statusText.textContent = "Network issue";
        setConfidenceBadge(null, false);
        saveConversation();
    } finally {
        sendBtn.disabled = false;
    }
}

input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        sendMessage();
    }
});

sendBtn.addEventListener("click", sendMessage);

clearBtn.addEventListener("click", () => {
    chatWindow.innerHTML = "";
    appendMessage("Chat cleared. Ask a new question whenever you are ready.", "bot");
    statusText.textContent = "Ready";
    setConfidenceBadge(null, false);
    saveConversation();
    input.focus();
});

quickQuestions.forEach((button) => {
    button.addEventListener("click", () => {
        input.value = button.dataset.question || "";
        input.focus();
    });
});

if (welcomeTime) {
    welcomeTime.textContent = formatTime();
}

restoreConversation();
if (!localStorage.getItem(STORAGE_KEY)) {
    saveConversation();
}
setConfidenceBadge(null, false);
