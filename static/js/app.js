// Connect the server with a WebSocket connection
const sessionId = Math.random().toString().substring(10);

// Detect if running in Google Cloud Shell or locally
const isCloudShell = window.location.hostname.includes('cloudshell') || 
                     window.location.hostname.includes('devshell');

// Determine WebSocket protocol and URL
let ws_protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
let ws_host = window.location.host;

// For Cloud Shell, ensure we use wss:// protocol
if (isCloudShell) {
  ws_protocol = "wss:";
  console.log("Detected Google Cloud Shell environment");
}

const ws_url = ws_protocol + "//" + ws_host + "/ws/" + sessionId;
console.log("WebSocket URL:", ws_url);

let websocket = null;

// Get DOM elements
const messageForm = document.getElementById("messageForm");
const messageInput = document.getElementById("message");
const messagesDiv = document.getElementById("messages");
const sendButton = document.getElementById("sendButton");
let currentMessageId = null;

// WebSocket handlers
function connectWebsocket() {
  // Connect websocket (text mode only)
  websocket = new WebSocket(ws_url + "?is_audio=false");

  // Handle connection open
  websocket.onopen = function () {
    console.log("WebSocket connection opened.");
    messagesDiv.innerHTML = '<p class="text-gray-500">Connected. Ready to analyze financial data...</p>';
    sendButton.disabled = false;
    addSubmitHandler();
  };

  // Handle incoming messages
  websocket.onmessage = function (event) {
    const message_from_server = JSON.parse(event.data);
    console.log("[AGENT TO CLIENT]", message_from_server);

    // Check if the turn is complete
    if (message_from_server.turn_complete === true) {
      currentMessageId = null;
      console.log("Turn completed - ready for next message");
      return;
    }

    // Check if interrupted
    if (message_from_server.interrupted === true) {
      currentMessageId = null;
      console.log("Turn interrupted");
      return;
    }

    // If it's text, display it
    if (message_from_server.mime_type === "text/plain") {
      // Add a new message for a new turn
      if (currentMessageId === null) {
        currentMessageId = Math.random().toString(36).substring(7);
        const messageWrapper = document.createElement("div");
        messageWrapper.className = "mb-4 p-4 bg-blue-50 rounded-lg";
        messageWrapper.id = "wrapper-" + currentMessageId;
        
        const messageLabel = document.createElement("div");
        messageLabel.className = "text-xs font-semibold text-blue-600 mb-2";
        messageLabel.textContent = "Agent Response:";
        messageWrapper.appendChild(messageLabel);
        
        const message = document.createElement("p");
        message.className = "text-gray-800 whitespace-pre-wrap";
        message.id = currentMessageId;
        messageWrapper.appendChild(message);
        
        messagesDiv.appendChild(messageWrapper);
      }

      // Add message text to the existing message element
      const message = document.getElementById(currentMessageId);
      if (message) {
        message.textContent += message_from_server.data;
      }

      // Scroll down to the bottom of the messagesDiv
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
  };

  // Handle connection close
  websocket.onclose = function () {
    console.log("WebSocket connection closed.");
    sendButton.disabled = true;
    messagesDiv.innerHTML = '<p class="text-red-500">Connection closed. Reconnecting...</p>';
    setTimeout(function () {
      console.log("Reconnecting...");
      connectWebsocket();
    }, 5000);
  };

  websocket.onerror = function (e) {
    console.log("WebSocket error: ", e);
    messagesDiv.innerHTML = '<p class="text-red-500">Connection error. Check console for details.</p>';
  };
}

// Initialize connection on page load
connectWebsocket();

// Add submit handler to the form
function addSubmitHandler() {
  messageForm.onsubmit = function (e) {
    e.preventDefault();
    const message = messageInput.value.trim();
    
    if (message) {
      // Display user message
      const userMessageWrapper = document.createElement("div");
      userMessageWrapper.className = "mb-4 p-4 bg-gray-100 rounded-lg";
      
      const userLabel = document.createElement("div");
      userLabel.className = "text-xs font-semibold text-gray-600 mb-2";
      userLabel.textContent = "You:";
      userMessageWrapper.appendChild(userLabel);
      
      const userMessage = document.createElement("p");
      userMessage.className = "text-gray-800";
      userMessage.textContent = message;
      userMessageWrapper.appendChild(userMessage);
      
      messagesDiv.appendChild(userMessageWrapper);
      messageInput.value = "";

      // Send message to server
      sendMessage({
        mime_type: "text/plain",
        data: message,
      });
      
      console.log("[CLIENT TO AGENT]", message);
      
      // Scroll to bottom
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    return false;
  };
}

// Send a message to the server as a JSON string
function sendMessage(message) {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    const messageJson = JSON.stringify(message);
    websocket.send(messageJson);
  } else {
    console.error("WebSocket is not open. Current state:", websocket?.readyState);
    messagesDiv.innerHTML += '<p class="text-red-500">Error: Not connected to server</p>';
  }
}
