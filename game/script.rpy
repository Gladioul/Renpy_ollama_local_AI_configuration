define e = Character('Eileen')
define p = Character('Me')

init python:
    import requests
    import subprocess
    import time
    OLLAMA_URL = "http://localhost:11434/api/generate"
    MODEL_NAME = "gemma3:1b"
    # New: Initialize persistent list for saved personalities
    if not hasattr(persistent, 'personalities'):
        persistent.personalities = []


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
        except requests.exceptions.ConnectionError:
            # Intentar iniciar ollama si no está corriendo
            try:
                subprocess.Popen(["ollama", "serve"])
            except Exception as e:
                return f"[Error al iniciar Ollama: {e}]"
            # Después de iniciar, esperar unos segundos e intentar de nuevo
            time.sleep(5)
            try:
                resp = requests.post(OLLAMA_URL, json=payload, timeout=20)
                resp.raise_for_status()
                data = resp.json()
                return data.get("response") or data.get("text") or str(data)
            except Exception as e2:
                return f"[Error tras intentar iniciar Ollama: {e2}]"
        except Exception as e:
            return f"[Error: {e}]"


    def dividir_en_bloques(texto, limite=32):
        """
        Divide el texto en bloques consecutivos de máximo 'limite' palabras.
        Los bloques intermedios terminan con '...' para indicar que continúa.
        """
        palabras = texto.split()
        bloques = []
        for i in range(0, len(palabras), limite):
            bloque = palabras[i:i+limite]
            if i + limite < len(palabras):
                bloques.append(" ".join(bloque) + "...")
            else:
                bloques.append(" ".join(bloque))
        return bloques

# Declaración de la imagen de fondo
image bg forest = "forest.png"

label start:
    scene bg forest

    show eileen happy
    $ history = []

    # New: Menu to choose personality method
    menu:
        "Enter a new personality prompt":
            jump enter_personality
        "Select a saved personality":
            jump select_personality

    label enter_personality:
        e "Enter a personality prompt for Eileen (e.g., 'You are a sarcastic AI assistant'), or leave empty for default."
        $ personality = renpy.input("Personality:")
        if personality == "":
            $ personality = "You are Eileen, a cheerful and helpful character in a visual novel. Respond in character."
        # New: Ask to save the personality
        menu:
            "Save this personality for future use?":
                $ persistent.personalities.append(personality)
                e "Personality saved!"
            "Don't save":
                pass
        jump start_done

    label select_personality:
        if not persistent.personalities:
            e "No saved personalities yet. Please enter a new one."
            jump enter_personality
        # New: Display menu with saved personalities
        $ options = [(p, p) for p in persistent.personalities] + [("Back", "back")]
        $ choice = renpy.display_menu(options)
        if choice == "back":
            jump start
        $ personality = choice
        jump start_done

    label start_done:
        # Continue to chat
        jump chat


label chat:
    e "Write something and I talk back. Leave it empty to exit."

    $ user = renpy.input("Your message:")

    if user == "":
        e "See you."
        return

    p "[user]"
    # Modified: Build full prompt with personality as system instruction
    $ full_prompt = personality + "\nRespond to: " + user
    $ reply = generar_con_ollama(full_prompt)

    python:
        for line in reply.splitlines():
            if line.strip():
                bloques = dividir_en_bloques(line)
                for bloque in bloques:
                    renpy.say(e, bloque)
                    history.append((user, bloque))  # Guardar cada bloque mostrado

    jump chat