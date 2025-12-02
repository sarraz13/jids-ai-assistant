let sessionId = '';
let userName = '';
let selectedFile = null;

function showNameScreen() {
  document.getElementById('landingScreen').classList.add('hidden');
  document.getElementById('nameScreen').classList.remove('hidden');
  setTimeout(() => document.getElementById('nameInput').focus(), 300);
}

function saveName() {
  const input = document.getElementById('nameInput');
  const name = input.value.trim();
  
  if (!name) {
    alert('Please enter your name');
    return;
  }
  
  userName = name;
  document.getElementById('nameScreen').classList.add('hidden');
  document.getElementById('chatContainer').classList.remove('hidden');
  document.getElementById('welcomeText').textContent = `Welcome, ${userName}!`;
  
  // Optional: Add initial greeting message
  addMessage(`Hello ${userName}! I'm Jids, your AI assistant. How can I help you today?`, 'assistant');
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) {
    selectedFile = file;
    const display = document.getElementById('fileNameDisplay');
    display.textContent = `📎 ${file.name}`;
    display.style.display = 'inline-block';
  }
}

async function sendMessage() {
  const input = document.getElementById('userInput');
  const message = input.value.trim();
  
  if (!message && !selectedFile) return;

  // Show user message
  if (message) {
    addMessage(message, 'user');
  }
  
  // Show file attachment indicator if file selected
  if (selectedFile) {
    addMessage(`📎 Attached: ${selectedFile.name}`, 'user');
  }
  
  input.value = '';

  try {
    const formData = new FormData();
    formData.append('message', message);
    
    // Only append session_id if it's not null/empty
    if (sessionId) {
      formData.append('session_id', sessionId);
    }
    
    if (selectedFile) {
      formData.append('file', selectedFile);
    }

    const response = await fetch('/api/agent/', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    if (response.ok) {
      sessionId = data.session_id;
      addMessage(data.assistant_message.content, 'assistant');
    } else {
      addMessage(`Error: ${data.error}`, 'assistant');
    }
  } catch (err) {
    addMessage(`Error: ${err.message}`, 'assistant');
  }
  
  // Reset file selection
  selectedFile = null;
  document.getElementById('fileInput').value = '';
  document.getElementById('fileNameDisplay').style.display = 'none';
}

function addMessage(text, role) {
  const messagesDiv = document.getElementById('messages');
  const msgDiv = document.createElement('div');
  msgDiv.className = 'message ' + role;
  msgDiv.textContent = text;
  messagesDiv.appendChild(msgDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Allow Enter key to send message
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('userInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });
});