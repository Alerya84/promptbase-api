from openai import OpenAI
from flask import Flask, request, jsonify
import json
import re

app = Flask(__name__)
client = OpenAI()

@app.route('/generate-prompts', methods=['POST'])
def generate_prompts():
    data = request.get_json()
    theme = data.get('theme')
    context = data.get('context')

    prompt_text = (
        f"Tu es un assistant PromptBase. "
        f"Génère un template avec des variables entre [crochets] pour le thème '{theme}' "
        f"et le contexte '{context}'. "
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
        ]
    )

    result_text = response.choices[0].message.content

    # On retire les balises markdown
    json_string = re.search(r'```json(.*?)```', result_text, re.DOTALL)
    if json_string:
        json_data = json_string.group(1).strip()
    else:
        json_data = result_text.strip()

    # On essaie de parser le JSON
    try:
        parsed_json = json.loads(json_data)
    except json.JSONDecodeError:
        parsed_json = {
            "template": "Error: Could not parse JSON.",
            "examples": [],
            "seo_title": "",
            "description": "",
            "buyer_tips": ""
        }

    return jsonify(parsed_json)

if __name__ == '__main__':
    app.run(debug=True)
