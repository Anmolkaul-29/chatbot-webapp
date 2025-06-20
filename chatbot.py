import os
from dotenv import load_dotenv  # type: ignore
from flask import Flask, request, jsonify, render_template_string  # type: ignore
from openai import OpenAI  # Updated SDK

load_dotenv()

client = OpenAI(
    api_key=os.getenv("TOGETHER_API_KEY"),
    base_url="https://api.together.xyz/v1"
)

with open("hierarchy.txt", "r", encoding="utf-8") as f:
    hierarchy_context = f.read()

app = Flask(__name__)

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GraphRAG Chat</title>
        <style>
            body {
                font-family: 'Segoe UI', sans-serif;
                background: #121212;
                color: #fff;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                height: 100vh;
                justify-content: space-between;
            }
            .chatbox {
                width: 90%;
                max-width: 700px;
                margin-top: 40px;
                background: #1f1f1f;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            }
            h2 {
                text-align: center;
                color: #00bcd4;
            }
            input {
                width: calc(100% - 100px);
                padding: 10px;
                font-size: 16px;
                border: none;
                border-radius: 6px;
                margin-right: 10px;
                background: #333;
                color: #fff;
            }
            button {
                padding: 10px 20px;
                background: #00bcd4;
                color: #fff;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }
            button:hover {
                background: #0097a7;
            }
            .response {
                margin-top: 20px;
                padding: 15px;
                background: #272727;
                border-radius: 8px;
                white-space: pre-wrap;
                max-height: 300px;
                overflow-y: auto;
            }
            footer {
                margin: 20px 0;
                color: #888;
                font-size: 14px;
            }
            .footer-style {
                font-family: 'Cursive', sans-serif;
                font-weight: bold;
                color: #00bcd4;
            }
        </style>
    </head>
    <body>
        <div class="chatbox">
            <h2>Ask the AI</h2>
            <div style="display: flex;">
                <input id="msg" placeholder="Ask a question">
                <button onclick="send()">Send</button>
            </div>
            <div id="res" class="response"></div>
        </div>
        <footer>
            Made by <span class="footer-style">Anmol Kaul</span>
        </footer>
        <script>
          async function send() {
            const msg = document.getElementById("msg").value;
            const resBox = document.getElementById("res");
            resBox.innerText = "Thinking...";
            const res = await fetch("/chat", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ message: msg })
            });
            const data = await res.json();
            resBox.innerText = data.reply || data.error;
            resBox.scrollTop = resBox.scrollHeight;
          }
        </script>
    </body>
    </html>
    """)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    prompt = f"Project Info:\n{hierarchy_context}\n\nQuestion: {user_input}"
    try:
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
