def modelo_disponible(model_name=None):
    """
    Verifica si el modelo está disponible localmente en la carpeta de modelos.
    """
    model_name = model_name or MODEL_NAME
    # El nombre del modelo se convierte en carpeta, por ejemplo: 'gemma3:1b' -> 'gemma3/1b'
    parts = model_name.split(":")
    if len(parts) == 2:
        model_dir = os.path.join(renpy.config.gamedir, "models", parts[0], parts[1])
    else:
        model_dir = os.path.join(renpy.config.gamedir, "models", model_name)
    # El modelo se considera disponible si existe un archivo model-card.json en la carpeta
    return os.path.isfile(os.path.join(model_dir, "model-card.json"))


def is_ollama_listening(host="localhost", port=11434, timeout=1):
    """
    Verifica si el servidor Ollama está escuchando en el puerto especificado.
    """
    import socket
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except Exception:
        return False

def start_ollama_serve():
    """
    Inicia el servidor Ollama en segundo plano si no está corriendo.
    """
    import subprocess, os, time
    gamedir = os.path.abspath(renpy.config.gamedir)
    ollama_exe = os.path.join(gamedir, "bin", "ollama.exe")
    models_dir = os.path.join(gamedir, "models")
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = models_dir
    # Lanzar en background
    subprocess.Popen([ollama_exe, "serve"], env=env, cwd=os.path.dirname(ollama_exe), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Esperar a que el puerto esté disponible
    for _ in range(30):
        if is_ollama_listening():
            return True
        time.sleep(1)
    return False

def descargar_modelo_async(model_name=None, on_finish=None, on_progress=None):
    """
    Descarga el modelo en un hilo aparte para no bloquear Ren'Py.
    Llama a on_finish(resultado, error) al terminar.
    Llama a on_progress(mensaje) para informar el progreso (opcional).
    """
    import threading
    def worker():
        import subprocess, os, time
        model_name_ = model_name or MODEL_NAME
        gamedir = os.path.abspath(renpy.config.gamedir)
        models_dir = os.path.join(gamedir, "models")
        ollama_exe = os.path.join(gamedir, "bin", "ollama.exe")
        env = os.environ.copy()
        env["OLLAMA_MODELS"] = models_dir
        if not os.path.isfile(ollama_exe):
            if on_progress:
                on_progress("No se encontró ollama.exe en bin/. Copia el ejecutable allí.")
            if on_finish:
                on_finish(False, "No se encontró ollama.exe en bin/. Copia el ejecutable allí.")
            return
        # Iniciar servidor si no está corriendo
        if not is_ollama_listening():
            if on_progress:
                on_progress("Iniciando el servidor Ollama...")
            start_ollama_serve()
            for _ in range(10):
                if is_ollama_listening():
                    break
                time.sleep(1)
            if not is_ollama_listening():
                if on_progress:
                    on_progress("No se pudo iniciar el servidor Ollama.")
                if on_finish:
                    on_finish(False, "No se pudo iniciar el servidor Ollama.")
                return
        if on_progress:
            on_progress(f"Descargando el modelo '{model_name_}'...")
        try:
            proc = subprocess.run([ollama_exe, "pull", model_name_], env=env, cwd=os.path.dirname(ollama_exe), capture_output=True, text=True)
            if proc.returncode != 0:
                if on_progress:
                    on_progress(f"Error al descargar el modelo: {proc.stderr.strip()} {proc.stdout.strip()}")
                if on_finish:
                    on_finish(False, proc.stderr.strip() + "\n" + proc.stdout.strip())
                return
            if on_progress:
                on_progress("¡Modelo descargado correctamente!")
            if on_finish:
                on_finish(True, None)
        except Exception as e:
            if on_progress:
                on_progress(f"Error inesperado: {str(e)}")
            if on_finish:
                on_finish(False, str(e))
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()



import requests
import subprocess
import socket
import time
import os
from hidden_prompt import  _merge_hidden_prompt  

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:1b"
# Comando para arrancar Ollama si está disponible en PATH.
# Puedes cambiar a ['ollama', 'serve'] u otra variante según tu instalación.
import renpy
# Usar el ejecutable local de Ollama en 'game/bin/ollama.exe'
OLLAMA_CMD = [os.path.join(renpy.config.gamedir, "bin", "ollama.exe"), "serve"]
# Tiempo máximo a esperar a que el servicio esté arriba (segundos)
OLLAMA_STARTUP_TIMEOUT = 10

def _is_ollama_listening(host="localhost", port=11434, timeout=1):
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except Exception:
        return False

def _start_ollama(cmd=None):
    cmd = cmd or OLLAMA_CMD
    # Verificar que el ejecutable local existe
    if not os.path.isfile(cmd[0]):
        return False, f"ollama executable not found at {cmd[0]}"
    # Configurar carpeta de modelos local
    models_dir = os.path.join(renpy.config.gamedir, "models")
    os.makedirs(models_dir, exist_ok=True)
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = models_dir
    try:
        # Lanzar en background, silenciar salida, con variable de entorno personalizada
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=os.getcwd(), env=env)
        return True, None
    except Exception as e:
        return False, str(e)

def _ensure_ollama_running(timeout=OLLAMA_STARTUP_TIMEOUT):
    # Si ya hay un listener, OK
    if _is_ollama_listening():
        return True, None
    # Intentar arrancar
    started, err = _start_ollama()
    if not started:
        return False, "could not start ollama: {}".format(err)
    # Esperar hasta que responda o se agote el timeout
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _is_ollama_listening():
            return True, None
        time.sleep(0.5)
    return False, "timeout waiting for ollama to start"

def generar_con_ollama(prompt, timeout=20):
    # Asegurarse de que el servicio esté activo antes de la petición
    ok, err = _ensure_ollama_running()
    if not ok:
        return "[Error: {}]".format(err)

    # Combinar con prompt oculto antes de hacer la petición
    combined_prompt = _merge_hidden_prompt(prompt)

    payload = {
        "model": MODEL_NAME,
        "prompt": combined_prompt,
        "stream": False
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        if resp.status_code == 404:
            return "[Error: El modelo solicitado no está disponible en Ollama o el endpoint no existe. Asegúrate de que el modelo 'gemma3:1b' esté cargado y disponible.]"
        resp.raise_for_status()
        data = resp.json()
        return data.get("response") or data.get("text") or str(data)
    except requests.exceptions.ConnectionError:
        return "[Error: No se pudo conectar con Ollama. ¿Está el servidor iniciado?]"
    except Exception as e:
        return "[Error inesperado: {}]".format(e)

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
