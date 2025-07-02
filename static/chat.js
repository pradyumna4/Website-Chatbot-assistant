// chat.js for Assistbot UI
const chatBox = document.getElementById("chat-box");
const messages = document.getElementById("chat-messages");
const input = document.getElementById("chat-input");
const typingIndicator = document.getElementById("typing-indicator");
const chatToggle = document.getElementById("chat-toggle");
const langSelect = document.getElementById("lang-select");
let isDragging = false, dragOffsetX = 0, dragOffsetY = 0;

function toggleChat() {
  if (chatBox.classList.contains("open")) {
    chatBox.classList.remove("open");
    chatBox.style.pointerEvents = "none";
    setTimeout(() => { chatBox.style.display = "none"; }, 300);
  } else {
    chatBox.style.display = "flex";
    setTimeout(() => {
      chatBox.classList.add("open");
      chatBox.style.pointerEvents = "auto";
    }, 10);
    chatBox.style.left = '';
    chatBox.style.top = '';
    chatBox.style.right = '20px';
    chatBox.style.bottom = '100px';
    if (!messages.hasChildNodes()) {
      setTimeout(() => addMessage("bot", "<b>Hi! I'm Assistbot.</b><br>How can I help you today?"), 200);
    }
  }
}

function addMessage(sender, text) {
  const msg = document.createElement("div");
  msg.className = `message ${sender}`;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.innerHTML = sender === "user" ? '<i class="fa fa-user"></i>' : '<i class="fa fa-robot"></i>';
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = text.replace(/\n/g, "<br>");
  if (sender === "user") {
    msg.appendChild(bubble);
    msg.appendChild(avatar);
  } else {
    msg.appendChild(avatar);
    msg.appendChild(bubble);
  }
  messages.appendChild(msg);
  messages.scrollTop = messages.scrollHeight;
}

function showTyping(show) {
  typingIndicator.style.display = show ? "flex" : "none";
  if (show) messages.scrollTop = messages.scrollHeight;
}

async function sendMessage() {
  const userText = input.value.trim();
  if (!userText) return;
  addMessage("user", userText);
  input.value = "";
  showTyping(true);
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userText, lang: langSelect.value })
    });
    const data = await res.json();
    showTyping(false);
    addMessage("bot", data.response);
  } catch (err) {
    showTyping(false);
    addMessage("bot", "⚠️ Couldn't reach the bot. Please try again later.");
  }
}

input.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});

function startDrag(e) {
  isDragging = true;
  const rect = chatBox.getBoundingClientRect();
  dragOffsetX = e.clientX - rect.left;
  dragOffsetY = e.clientY - rect.top;
  document.addEventListener('mousemove', dragMove);
  document.addEventListener('mouseup', stopDrag);
}
function dragMove(e) {
  if (!isDragging) return;
  chatBox.style.right = 'auto';
  chatBox.style.left = (e.clientX - dragOffsetX) + 'px';
  chatBox.style.top = (e.clientY - dragOffsetY) + 'px';
  chatBox.style.bottom = 'auto';
}
function stopDrag() {
  isDragging = false;
  document.removeEventListener('mousemove', dragMove);
  document.removeEventListener('mouseup', stopDrag);
}
window.addEventListener('resize', () => {
  chatBox.style.left = '';
  chatBox.style.top = '';
  chatBox.style.right = '20px';
  chatBox.style.bottom = '100px';
});

// --- Speech Recognition (Speech-to-Text) ---
const micBtn = document.getElementById("mic-btn");
const micStatus = document.getElementById("mic-status");
let recognition;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  micBtn.onclick = () => {
    recognition.lang = langSelect.value + "-IN";
    recognition.start();
    micBtn.classList.add("listening");
    micStatus.style.display = "inline";
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    micBtn.classList.remove("listening");
    micStatus.style.display = "none";
    input.value = transcript;
    setTimeout(() => { sendMessage(); }, 400);
  };
  recognition.onerror = () => {
    micBtn.classList.remove("listening");
    micStatus.style.display = "none";
  };
  recognition.onend = () => {
    micBtn.classList.remove("listening");
    micStatus.style.display = "none";
  };
} else {
  micBtn.style.display = "none";
  micStatus.style.display = "none";
}

// --- Text-to-Speech (SpeechSynthesis) ---
const speakBtn = document.getElementById("speak-btn");
let lastBotMsg = "";
function speak(text) {
  if (!window.speechSynthesis) return;
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = "en-US";
  window.speechSynthesis.speak(utter);
}
speakBtn.onclick = () => {
  if (lastBotMsg) speak(lastBotMsg);
};

// Save last bot message for TTS
const origAddMessage = addMessage;
addMessage = function(sender, text) {
  origAddMessage(sender, text);
  if (sender === "bot") lastBotMsg = text.replace(/<[^>]+>/g, '');
};
