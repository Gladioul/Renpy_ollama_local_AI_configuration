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
        from ollama import modelo_disponible, descargar_modelo_async, MODEL_NAME
        if modelo_disponible():
            _descarga_exitosa = True
            _descarga_error = ""
        else:
            # Usar una variable para capturar el resultado del hilo
            resultado = {"success": None, "error": None}
            def on_finish(success, error):
                resultado["success"] = success
                resultado["error"] = error
            descargar_modelo_async(MODEL_NAME, on_finish)
            # Esperar a que termine el hilo (máx 60s)
            import time
            timeout = 60
            waited = 0
            while resultado["success"] is None and waited < timeout:
                time.sleep(0.2)
                waited += 0.2
            _descarga_exitosa = resultado["success"]
            _descarga_error = resultado["error"] or ""
    if not _descarga_exitosa:
        e "No se pudo descargar el modelo. Error: [_descarga_error] Por favor, revisa tu conexión, el nombre del modelo y que ollama.exe esté en bin/."
        return
    else:
        e "¡Modelo descargado correctamente!"
        return
