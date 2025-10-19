import requests
import subprocess
import socket
import time
import shutil
import os
from hidden_prompt import load_hidden_prompt, save_hidden_prompt, _merge_hidden_prompt  

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:1b"
# Comando para arrancar Ollama si está disponible en PATH.
# Puedes cambiar a ['ollama', 'serve'] u otra variante según tu instalación.
OLLAMA_CMD = ["ollama", "serve"]
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
    # Verificar disponibilidad del ejecutable
    if shutil.which(cmd[0]) is None:
        return False, "ollama executable not found in PATH"
    try:
        # Lanzar en background, silenciar salida
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=os.getcwd())
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
        resp.raise_for_status()
        data = resp.json()
        return data.get("response") or data.get("text") or str(data)
    except Exception as e:
        return "[Error: {}]".format(e)

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
