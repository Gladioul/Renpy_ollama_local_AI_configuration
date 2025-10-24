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
    call descargar_modelo_label

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
                    # Escape square brackets so Ren'Py doesn't try to evaluate
                    # inline substitutions like [Error: ...]. Store the original
                    # text in history but show the escaped version.
                    safe_bloque = bloque.replace('[', '[[').replace(']', ']]')
                    renpy.say(e, safe_bloque)
                    history.append((user, bloque))  # Guardar cada bloque mostrado

    jump chat

label descargar_modelo_label:
    python:
        from ollama import modelo_disponible, descargar_modelo_simple, MODEL_NAME
        if modelo_disponible():
            _descarga_exitosa = True
            _descarga_error = ""
        else:
            _descarga_exitosa = descargar_modelo_simple(MODEL_NAME)
            try:
                from ollama import descargar_modelo_simple as dms
                _descarga_error = getattr(dms, 'last_error', "")
            except Exception:
                _descarga_error = ""
    if not _descarga_exitosa:
        e "No se pudo descargar el modelo. Error: [_descarga_error] Por favor, revisa tu conexión, el nombre del modelo y que ollama.exe esté en bin/."
        return
    else:
        e "¡Modelo descargado correctamente!"
        return

screen barra_progreso_ollama():
    frame:
        xalign 0.5
        yalign 0.5
        has vbox
        text "[store._ollama_status]" xalign 0.5
        text "Descargando modelo... [store._ollama_progress]%" xalign 0.5
        bar value store._ollama_progress range 100 xmaximum 400 xalign 0.5
        if store._ollama_error_msg:
            text "[store._ollama_error_msg]" color "#f44" xalign 0.5