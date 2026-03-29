from flask import Flask, request, jsonify, render_template_string
from astra import ai_chat, login, get_weather, get_news
import threading
import os

app = Flask(__name__)

# --------- MOBILE UI (HTML) ---------
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Astra AI - Level 6</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0b0e14; color: #00d4ff; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
        .container { width: 90%; max-width: 400px; background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; box-shadow: 0 0 20px rgba(0, 212, 255, 0.2); border: 1px solid rgba(0, 212, 255, 0.3); }
        h1 { text-align: center; font-size: 24px; margin-bottom: 20px; text-shadow: 0 0 10px #00d4ff; }
        #chat-box { height: 300px; overflow-y: auto; background: rgba(0, 0, 0, 0.3); padding: 10px; border-radius: 10px; margin-bottom: 15px; display: flex; flex-direction: column; }
        .msg { margin: 5px 0; padding: 8px 12px; border-radius: 10px; max-width: 80%; }
        .user { align-self: flex-end; background: #00d4ff; color: #0b0e14; }
        .astra { align-self: flex-start; background: rgba(255, 255, 255, 0.1); color: #fff; }
        .input-area { display: flex; gap: 10px; }
        input { flex: 1; padding: 10px; border-radius: 5px; border: none; background: #1a1f26; color: white; outline: none; }
        button { padding: 10px 20px; border-radius: 5px; border: none; background: #00d4ff; color: #0b0e14; font-weight: bold; cursor: pointer; }
        button:active { transform: scale(0.95); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ Astra Level 6</h1>
        <div id="chat-box"></div>
        <div class="input-area">
            <input type="text" id="user-input" placeholder="Ask Astra...">
            <button onclick="sendMsg()">Send</button>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chat-box');
        const userInput = document.getElementById('user-input');

        function appendMsg(text, type) {
            const div = document.createElement('div');
            div.className = 'msg ' + type;
            div.innerText = text;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function sendMsg() {
            const text = userInput.value.trim();
            if (!text) return;

            appendMsg(text, 'user');
            userInput.value = '';

            try {
                const res = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                const data = await res.json();
                appendMsg(data.reply, 'astra');
            } catch (e) {
                appendMsg('Error connecting to Astra ❌', 'astra');
            }
        }

        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMsg();
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_UI)

# --------- MOBILE AUTH ---------
@app.route("/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    if login(username, password):
        return jsonify({"status": "success", "message": f"Welcome {username}"})
    else:
        return jsonify({"status": "error", "message": "Invalid Credentials"}), 401

# --------- ASK ASTRA ---------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("text")
    username = data.get("username", "akram") # Default for mobile app
    
    if not user_input:
        return jsonify({"error": "No input text provided"}), 400
    
    # Process Command via AI
    response = ai_chat(user_input)
    
    return jsonify({
        "reply": response,
        "status": "Astra Thinking... 🧠"
    })

# --------- GET INFO ---------
@app.route("/weather", methods=["GET"])
def weather():
    city = request.args.get("city", "Delhi")
    return jsonify({"info": get_weather(city)})

@app.route("/news", methods=["GET"])
def news():
    return jsonify({"articles": get_news()})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Astra Mobile API starting at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
