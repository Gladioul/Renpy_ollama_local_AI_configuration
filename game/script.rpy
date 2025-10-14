# game/script.rpy
define e = Character('Eileen')
define p = Character('Me')

init python:
    import requests
    OLLAMA_URL = "http://localhost:11434/api/generate"
    MODEL_NAME = "gemma3:1b"

    def generar_con_ollama(prompt):
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
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
    e "Write somethin and I talk back. Leave it empty to exit."

    $ user = renpy.input("Your message:")

    if user == "":
        e "See you."
        return

    p "[user]"
    $ reply = generar_con_ollama(user)
    $ history.append((user, reply))

    e "[reply]"
    jump chat
