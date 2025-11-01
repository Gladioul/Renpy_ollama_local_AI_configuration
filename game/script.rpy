define e = Character('Concepción', image='concepcion')
define p = Character('Me')

image forest = "forest.png"

# Concepción is a portrait image (720x1920). The game resolution is 1920x1080
# We scale the image so its height matches the screen height (1080px).
# Scale factor = 1080 / 1920 = 0.5625 -> width becomes 720 * 0.5625 = 405px.
# Using a Transform keeps the image centered vertically and horizontally.
image concepcion = Transform("images/concepcion.png", xalign=0.5, yalign=0.5, zoom=0.5625)

init python:
    # Import functions from the module ollama located in the game folder
    from script_functions import split_into_blocks
    from ollama import generate_with_ollama, is_model_available, download_model_async

label start:
    scene forest
    # Show the protagonist image, scaled to screen height and centered
    show concepcion
    $ history = []
    call download_model_label from _call_download_model_label

label chat:
    e "Write something and I talk back. Leave it empty to exit."

    $ user = renpy.input("Your message:")

    if user == "":
        e "See you."
        return

    p "[user]"
    $ reply = generate_with_ollama(user)

    python:
        for line in reply.splitlines():
            if line.strip():
                blocks = split_into_blocks(line)
                for block in blocks:
                    # Escape square brackets so Ren'Py doesn't try to evaluate
                    # inline substitutions like [Error: ...]. Store the original
                    # text in history but show the escaped version.
                    safe_block = block.replace('[', '[[').replace(']', ']]')
                    renpy.say(e, safe_block)
                    history.append((user, block))  # Save each displayed block

    jump chat

label download_model_label:
    python:
        from ollama import is_model_available, download_model_async, MODEL_NAME
        if is_model_available():
            _download_successful = True
            _download_error = ""
        else:
            # Use a variable to capture the thread result
            result = {"success": None, "error": None}
            def on_finish(success, error):
                result["success"] = success
                result["error"] = error
            download_model_async(MODEL_NAME, on_finish)
            # Wait for the thread to finish (max 60s)
            import time
            timeout = 60
            waited = 0
            while result["success"] is None and waited < timeout:
                time.sleep(0.2)
                waited += 0.2
            _download_successful = result["success"]
            _download_error = result["error"] or ""
    if not _download_successful:
        e "Could not download the model. Error: [_download_error] Please check your connection, the model name, and that ollama.exe is in bin/."
        return
    else:
        e "Model downloaded successfully!"
        return
