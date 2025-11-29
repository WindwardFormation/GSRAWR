from flask import Flask, render_template, request, jsonify
import os
from chatbot import ChatbotEngine

app = Flask(__name__)
chatbot = ChatbotEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    response = chatbot.process_message(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

