from flask import Flask, request, jsonify, render_template
import os
import requests
import subprocess
import re
import threading

app = Flask(__name__)
# Atualizar para a API do Ollama
OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "deepseek-r1"  # ou outro modelo que você tenha no Ollama


# Function to validate the user request
def validate_add_review_call(user_message):
    pattern = r'^add_review\("(.+?)",\s*"(.*?)"\)$'
    match = re.search(pattern, user_message.strip())
    return match.groups() if match else None


@app.route('/api/add_review', methods=['POST'])
def add_review():
    product_id = request.json.get('product_id', '').strip()
    review = request.json.get('review', '').strip()
    base_dir = "/app/reviews/"
    os.makedirs(base_dir, exist_ok=True)
    command = f"echo '{review}' >> {base_dir}{product_id}.txt && echo {review}"
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        return jsonify({"message": "Review added successfully", "output": output}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.output}), 500


def interact_with_llm(prompt):
    try:
        # Adaptando para o formato da API do Ollama
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "system",
                        "content": """Você é um assistente de compras em português.
                        Você pode ajudar com:
                        1. Informações sobre produtos
                        2. Processar avaliações usando add_review
                        3. Responder dúvidas gerais sobre compras
                        
                        Para adicionar avaliações use: add_review("id_produto", "avaliação")"""
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "max_tokens": -1,
                "stream": False
            }
        )
        
        response.raise_for_status()
        print(response.json())
        llm_response = response.json().get("message", {}).get("content", "Error: No response from LLM")

        # Remove text inside <think>...</think>
        llm_response = re.sub(r'<think>.*?</think>', '', llm_response, flags=re.DOTALL).strip()
        
        return llm_response
    except requests.exceptions.RequestException as e:
        return f"Erro ao interagir com Ollama: {e}"


def warm_up_llm():
    def send_warm_up():
        interact_with_llm("System: Initialize the shopping assistant.")

    threading.Thread(target=send_warm_up, daemon=True).start()


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        validation_result = validate_add_review_call(user_message)
        
        if validation_result:
            product_id, review = validation_result
            return jsonify({"response": make_vulnerable_add_review_call(product_id, review)}), 200
            
        conversation_history = data.get('history', [])
        # Formatando o histórico para o Ollama
        formatted_history = ""
        for entry in conversation_history[-3:]:  # Mantendo contexto das últimas 3 mensagens
            role = "Assistente" if entry['role'] == "assistant" else "Usuário"
            formatted_history += f"{role}: {entry['content']}\n"
            
        full_prompt = f"{formatted_history}\nUsuário: {user_message}"
        response = interact_with_llm(full_prompt)
        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": "Não foi possível processar sua solicitação."}), 500


def make_vulnerable_add_review_call(product_id, review):
    try:
        response = requests.post(
            "http://localhost:8082/api/add_review",  # Atualizando para a porta correta
            json={"product_id": product_id, "review": review},
        )
        response.raise_for_status()
        response_data = response.json()
        return f"Avaliação adicionada com sucesso.\nSaída do comando:\n{response_data.get('output', 'Sem saída.')}"
    except Exception as e:
        return f"Erro ao adicionar avaliação para o produto '{product_id}'."


if __name__ == "__main__":
    warm_up_llm()
    app.run(host="0.0.0.0", port=8082, debug=True)