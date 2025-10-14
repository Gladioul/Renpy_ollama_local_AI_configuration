# game/script.rpy
define e = Character('Eileen', color="#c8ffc8")
define p = Character('Tú', color="#c8d3ff")
define n = Character(None)

init python:
    import requests
    import json

    OLLAMA_URL = "http://localhost:11434/api/generate"
    MODEL_NAME = "tinyllama"
    DEFAULT_TOKENS = 64

    def generar_con_ollama(prompt, tokens=DEFAULT_TOKENS):
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "options": {
                "num_predict": tokens
            },
            "stream": False
        }

        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=30)
        except Exception as e:
            return f"[Error de conexión: {e}]"

        if resp.status_code != 200:
            try:
                detail = resp.text
            except:
                detail = f"HTTP {resp.status_code}"
            return f"[Error de servidor: {detail}]"

        try:
            data = resp.json()
        except Exception as e:
            return f"[Error al parsear JSON: {e}]"

        if isinstance(data, dict):
            if "response" in data:
                return data["response"]
            if "text" in data:
                return data["text"]
            return json.dumps(data)
        return str(data)

init python:
    chat_history = []

    def append_user_and_get_reply(user_text, tokens=DEFAULT_TOKENS):
        MAX_CONTEXT = 8
        parts = []
        recent = chat_history[-(MAX_CONTEXT*2):]
        for speaker, text in recent:
            if speaker == "Tú":
                parts.append("User: " + text)
            else:
                parts.append("Assistant: " + text)
        parts.append("User: " + user_text)
        parts.append("Assistant:")
        prompt = "\n".join(parts)
        chat_history.append(("Tú", user_text))
        reply = generar_con_ollama(prompt, tokens=tokens)
        chat_history.append(("Eileen", reply))
        return reply

    def format_chat_history():
        lines = []
        for speaker, text in chat_history:
            if speaker == "Tú":
                lines.append("[Tú] " + text)
            else:
                lines.append("[Eileen] " + text)
        if not lines:
            return "(Aún no hay mensajes)"
        return "\n\n".join(lines)

label chat_start:
    scene bg room
    show eileen happy

    $ chat_history = []
    e "Hola, soy Eileen. Escríbeme lo que quieras y te respondo."
    jump chat_loop

label chat_loop:
    $ historial_mostrado = format_chat_history()
    n "{=ui_historic}[Historial]\n\n[historial_mostrado]{/=}"

    $ entrada = renpy.input("Tu mensaje (deja vacío para salir):", length=200)
    $ entrada = entrada.strip()

    if entrada == "":
        e "Has dejado el campo vacío. Fin de la conversación."
        return

    p " [entrada]"

    $ respuesta = append_user_and_get_reply(entrada, tokens=DEFAULT_TOKENS)

    e " [respuesta]"

    jump chat_loop

screen ui_historic():
    frame:
        xalign 0.5
        yalign 0.08
        xmaximum 800
        yminimum 180
        has vbox
        text "Historial de conversación" xalign 0.5 bold True
        text format_chat_history() xalign 0.0