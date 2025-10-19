define e = Character('Eileen')
define p = Character('Me')

init python:
    # Importar funciones desde el módulo ollama que está en la carpeta game
    from ollama import generar_con_ollama, dividir_en_bloques

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

label start:
    scene bg room
    show eileen happy
    $ history = []

label chat:
    e "Write something and I talk back. Leave it empty to exit."

    $ user = renpy.input("Your message:")

    if user == "":
        e "See you."
        return

    p "[user]"
    $ reply = generar_con_ollama(user)

    python:
        for line in reply.splitlines():
            if line.strip():
                bloques = dividir_en_bloques(line)
                for bloque in bloques:
                    renpy.say(e, bloque)
                    history.append((user, bloque))  # Guardar cada bloque mostrado

    jump chat