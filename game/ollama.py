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

def descargar_modelo_con_progreso(model_name=None, progress_callback=None):
    """
    Descarga el modelo usando ollama.exe pull <modelo> y reporta el progreso y estado por callback.
    """
    import threading
    import re
    import socket
    import os
    model_name = model_name or MODEL_NAME
    models_dir = os.path.join(renpy.config.gamedir, "models")
    ollama_exe = os.path.join(renpy.config.gamedir, "bin", "ollama.exe")
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = models_dir
    # Verificar que el ejecutable existe
    if not os.path.isfile(ollama_exe):
        if progress_callback:
            progress_callback(-1, status="Error ejecutable", error_msg="No se encontró ollama.exe en bin/. Copia el ejecutable allí.")
        return False
    try:
        if progress_callback:
            progress_callback(0, status="Conectando...")
        proc = subprocess.Popen([ollama_exe, "pull", model_name], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        percent = 0
        status = "Descargando..."
        modelo_no_existe = False
        for line in proc.stdout:
            # Buscar porcentaje y estado en la salida
            m = re.search(r"(Pulling|Extracting|Verifying|Unpacking|Copying|Downloaded|Digest|Already up to date|Error|Failed|Complete)[^\d]*(\d+)?%?", line)
            if m:
                estado = m.group(1)
                if estado == "Pulling":
                    status = "Descargando..."
                elif estado == "Extracting":
                    status = "Extrayendo..."
                elif estado == "Verifying":
                    status = "Verificando..."
                elif estado == "Unpacking":
                    status = "Desempaquetando..."
                elif estado == "Copying":
                    status = "Copiando..."
                elif estado == "Downloaded":
                    status = "Descarga finalizada."
                elif estado == "Digest":
                    status = "Verificando integridad..."
                elif estado == "Already up to date":
                    status = "Ya actualizado."
                elif estado == "Complete":
                    status = "¡Completado!"
                elif estado == "Error" or estado == "Failed":
                    status = "Error"
                else:
                    status = estado
                if m.group(2):
                    percent = int(m.group(2))
                if progress_callback:
                    progress_callback(percent, status=status)
            # Si hay error textual
            if "not found" in line.lower() or "no such model" in line.lower():
                modelo_no_existe = True
                if progress_callback:
                    progress_callback(-1, status="Modelo no encontrado", error_msg=f"El modelo '{model_name}' no existe en Ollama. Verifica el nombre.")
            elif "error" in line.lower() or "failed" in line.lower() or "connection refused" in line.lower() or "could not resolve" in line.lower() or "no such host" in line.lower():
                if progress_callback:
                    progress_callback(-1, status="Error de conexión", error_msg="No se pudo conectar para descargar el modelo. Revisa tu conexión a internet o firewall.")
        proc.wait()
        if modelo_no_existe:
            return False
        if proc.returncode == 0:
            if progress_callback:
                progress_callback(100, status="¡Completado!")
            return True
        else:
            if progress_callback:
                progress_callback(-1, status="Error", error_msg=f"Fallo en la descarga (código {proc.returncode}). Intenta de nuevo o revisa tu conexión.")
            return False
    except Exception as e:
        # Si es un error de red, mensaje claro
        msg = str(e)
        if isinstance(e, OSError) and ("network" in msg.lower() or "connection" in msg.lower() or "internet" in msg.lower()):
            msg = "No se pudo conectar para descargar el modelo. Revisa tu conexión a internet o firewall."
        if progress_callback:
            progress_callback(-1, status="Error de conexión", error_msg=msg)
        return False

def _is_ollama_listening(host="localhost", port=11434, timeout=1):
    import socket
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except Exception:
        return False

def _start_ollama_serve():
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
        if _is_ollama_listening():
            return True
        time.sleep(1)
    return False

def descargar_modelo_simple(model_name=None):
    """
    Inicia el servidor Ollama si es necesario y descarga el modelo de forma síncrona y robusta.
    Devuelve True si la descarga fue exitosa, False si falló.
    """
    import subprocess
    import os
    import time
    model_name = model_name or MODEL_NAME
    gamedir = os.path.abspath(renpy.config.gamedir)
    models_dir = os.path.join(gamedir, "models")
    ollama_exe = os.path.join(gamedir, "bin", "ollama.exe")
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = models_dir
    if not os.path.isfile(ollama_exe):
        descargar_modelo_simple.last_error = "No se encontró ollama.exe en bin/. Copia el ejecutable allí."
        return False
    # Iniciar servidor si no está corriendo
    if not _is_ollama_listening():
        _start_ollama_serve()
        # Esperar unos segundos extra por si acaso
        for _ in range(10):
            if _is_ollama_listening():
                break
            time.sleep(1)
        if not _is_ollama_listening():
            descargar_modelo_simple.last_error = "No se pudo iniciar el servidor Ollama."
            return False
    try:
        proc = subprocess.run([ollama_exe, "pull", model_name], env=env, cwd=os.path.dirname(ollama_exe), capture_output=True, text=True)
        if proc.returncode != 0:
            descargar_modelo_simple.last_error = proc.stderr.strip() + "\n" + proc.stdout.strip()
            return False
        return True
    except Exception as e:
        descargar_modelo_simple.last_error = str(e)
        return False

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
