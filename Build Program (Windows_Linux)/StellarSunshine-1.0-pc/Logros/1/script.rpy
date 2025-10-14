define e = Character('Eileen')

init python:
    import requests
    import json

    def generar_con_ollama(prompt, tokens=16):
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "tinyllama",
            "prompt": prompt,
            "options": {
                "num_predict": tokens
            },
            "stream": False  # desactiva streaming para facilitar el parseo
        }

        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return "Error al generar texto."
        except Exception as e:
            return f"Error de conexión: {e}"

label start:

    scene bg room
    show eileen happy

    $ prompt = "Texto generado por la IA: "
    $ tokens_to_generate = 16

    e "Generando texto, por favor espera... {nw}"

    $ reply = generar_con_ollama(prompt, tokens_to_generate)

    jump loop

label loop:

    e "Prompt: [prompt]"
    e "Respuesta: [reply]"

    jump loop