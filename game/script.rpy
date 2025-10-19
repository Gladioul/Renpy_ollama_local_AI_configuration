define e = Character('Concepción')
define p = Character('Me')

image forest = "forest.png"

init python:
    # Importar funciones desde el módulo ollama que está en la carpeta game
    from ollama import generar_con_ollama, dividir_en_bloques

label start:
    scene forest
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