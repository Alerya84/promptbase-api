from openai import OpenAI
from flask import Flask, request, jsonify
import json
import re

app = Flask(__name__)
client = OpenAI()

@app.route('/generate', methods=['POST'])
def generate_prompts():
    data = request.get_json()
    theme = data.get('theme')
    context = data.get('context')
    variables = data.get('variables', [])  # Ajout ici : récupère une liste de variables
    temperature = 1.1

    # On prépare la chaîne de variables pour l’intégrer au prompt
    variable_string = ', '.join(f'[{v}]' for v in variables) if variables else "[variable1], [variable2]"

    prompt_text = (
        f"Tu es un assistant Midjourney. "
        f"Génère un template avec les variables suivantes : {variable_string} "
        f"pour le thème '{theme}' et le contexte '{context}'. "
        f"Propose aussi 9 exemples variés, un titre SEO de 40 caractères max, "
        f"une description en anglais (500 caractères max), "
        f"et des conseils pour les acheteurs. "
        f"Réponds uniquement en JSON structuré ainsi : "
        f"{{\"template\":\"...\",\"examples\":[\"...\",\"...\"],\"seo_title\":\"...\",\"description\":\"...\",\"buyer_tips\":\"...\"}}"
    )
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Tu es un assistant créatif pour PromptBase."},
            {"role": "user", "content": prompt_text}
        ],
        temperature=temperature
    )

    result_text = response.choices[0].message.content

    json_string = re.search(r'```json(.*?)```', result_text, re.DOTALL)
    if json_string:
        json_data = json_string.group(1).strip()
    else:
        json_data = result_text.strip()

    try:
        parsed_json = json.loads(json_data)
        parsed_json["status"] = "draft"  # Ajout ici : status du pack
    except json.JSONDecodeError:
        parsed_json = {
            "template": "Error: Could not parse JSON.",
            "examples": [],
            "seo_title": "",
            "description": "",
            "buyer_tips": "",
            "status": "error"
        }

    return jsonify(parsed_json)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)
