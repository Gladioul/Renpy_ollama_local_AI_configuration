# Declaración de personajes
define e = Character("Eileen")

# Inicialización de Python para usar Transformers desde lib/Transformers
init python:
    import sys
    import os

    # Ruta al código fuente de Transformers clonado
    transformers_path = os.path.abspath("lib/Transformers/src")
    sys.path.append(transformers_path)

    # Importar desde Transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

    # Cargar el modelo Gemma
    tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b-it")
    model = AutoModelForCausalLM.from_pretrained("google/gemma-2b-it")
    generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

    # Función para generar texto
    def generar_texto(prompt, max_length=100):
        resultado = generator(prompt, max_length=max_length, do_sample=True)
        return resultado[0]["generated_text"]

# Inicio del juego
label start:

    scene bg room
    show eileen happy

    # Prompt para Gemma
    $ entrada = "Saluda al jugador y explícale cómo crear una historia en Ren'Py."
    $ respuesta = generar_texto(entrada)

    # Mostrar el texto generado
    e "[respuesta]"

    return