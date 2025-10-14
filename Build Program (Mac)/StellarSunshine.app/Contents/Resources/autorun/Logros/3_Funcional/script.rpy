# game/script.rpy
define e = Character('Eileen')
define p = Character('Tú')

init python:
    import requests
    OLLAMA_URL = "http://localhost:11434/api/generate"
    MODEL_NAME = "tinyllama"
    DEFAULT_TOKENS = 64

    def generar_con_ollama(prompt, tokens=DEFAULT_TOKENS):
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "options": {"num_predict": tokens},
            "stream": False
        }
        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response") or data.get("text") or str(data)
        except Exception as e:
            return "[Error: {}]".format(e)

label start:
    scene bg room
    show eileen happy
    $ history = []  # lista simple de (usuario, ia)

label chat:
    e "Escribe algo y te respondo. Deja vacío para salir."
    $ user = renpy.input("Tu mensaje:", length=200).strip()
    if user == "":
        e "Hasta luego."
        return

    p "[user]"
    $ prompt = "User: " + user + "\nAssistant:"
    $ reply = generar_con_ollama(prompt, tokens=DEFAULT_TOKENS)
    $ history.append((user, reply))

    e "[reply]"
    jump chat