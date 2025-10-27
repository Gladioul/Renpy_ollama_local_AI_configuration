import requests
import subprocess
import socket
import time
import os
from hidden_prompt import  _merge_hidden_prompt  

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen:1.8b"

# MODEL_NAME = "qwen3:1.7b"
# MODEL_NAME = "gemma3:1b"

# Command to start Ollama if available in PATH.
# You can change to ['ollama', 'serve'] or another variant depending on your installation.

def get_ollama_cmd():
    import renpy
    return [os.path.join(renpy.config.gamedir, "bin", "ollama.exe"), "serve"]

def is_model_available(model_name=None):
    """
    Checks if the model is available locally in the models folder.
    """
    import renpy
    model_name = model_name or MODEL_NAME
    parts = model_name.split(":")
    if len(parts) == 2:
        model_dir = os.path.join(renpy.config.gamedir, "models", parts[0], parts[1])
    else:
        model_dir = os.path.join(renpy.config.gamedir, "models", model_name)
    # The model is considered available if a model-card.json file exists in the folder
    return os.path.isfile(os.path.join(model_dir, "model-card.json"))


def is_ollama_listening(host="localhost", port=11434, timeout=1):
    """
    Checks if the Ollama server is listening on the specified port.
    """
    import socket
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except Exception:
        return False

def start_ollama_server():
    """
    Starts the Ollama server in the background if it is not running.
    """
    import renpy
    gamedir = os.path.abspath(renpy.config.gamedir)
    ollama_exe = os.path.join(gamedir, "bin", "ollama.exe")
    models_dir = os.path.join(gamedir, "models")
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = models_dir
    # Launch in background
    subprocess.Popen(
        [ollama_exe, "serve"],
        env=env,
        cwd=os.path.dirname(ollama_exe),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    # Wait for the port to be available
    for _ in range(30):
        if is_ollama_listening():
            return True
        time.sleep(1)
    return False

def download_model_async(model_name=None, on_finish=None, on_progress=None):
    """
    Downloads the model in a separate thread to avoid blocking Ren'Py.
    Calls on_finish(result, error) upon completion.
    Calls on_progress(message) to report progress (optional).
    """
    import threading
    def worker():
        import renpy
        model_name_ = model_name or MODEL_NAME
        gamedir = os.path.abspath(renpy.config.gamedir)
        models_dir = os.path.join(gamedir, "models")
        ollama_exe = os.path.join(gamedir, "bin", "ollama.exe")
        env = os.environ.copy()
        env["OLLAMA_MODELS"] = models_dir
        if not os.path.isfile(ollama_exe):
            if on_progress:
                on_progress("Ollama.exe not found in bin/. Please copy the executable there.")
            if on_finish:
                on_finish(False, "Ollama.exe not found in bin/. Please copy the executable there.")
            return
        # Start server if not running
        if not is_ollama_listening():
            if on_progress:
                on_progress("Starting the Ollama server...")
            start_ollama_server()
            for _ in range(10):
                if is_ollama_listening():
                    break
                time.sleep(1)
            if not is_ollama_listening():
                if on_progress:
                    on_progress("Could not start the Ollama server.")
                if on_finish:
                    on_finish(False, "Could not start the Ollama server.")
                return
        if on_progress:
            on_progress(f"Downloading the model '{model_name_}'...")
        try:
            proc = subprocess.run(
                [ollama_exe, "pull", model_name_],
                env=env,
                cwd=os.path.dirname(ollama_exe),
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if proc.returncode != 0:
                if on_progress:
                    on_progress(f"Error downloading the model: {proc.stderr.strip()} {proc.stdout.strip()}")
                if on_finish:
                    on_finish(False, proc.stderr.strip() + "\n" + proc.stdout.strip())
                return
            if on_progress:
                on_progress("Model downloaded successfully!")
            if on_finish:
                on_finish(True, None)
        except Exception as e:
            if on_progress:
                on_progress(f"Unexpected error: {str(e)}")
            if on_finish:
                on_finish(False, str(e))
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

def _is_ollama_listening(host="localhost", port=11434, timeout=1):
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except Exception:
        return False

def _start_ollama(cmd=None):
    cmd = cmd or get_ollama_cmd()
    # Check that the local executable exists
    if not os.path.isfile(cmd[0]):
        return False, f"ollama executable not found at {cmd[0]}"
    # Set up local models folder
    models_dir = os.path.join(renpy.config.gamedir, "models")
    os.makedirs(models_dir, exist_ok=True)
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = models_dir
    try:
        # Launch in background, silence output, with custom environment variable
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=os.getcwd(),
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True, None
    except Exception as e:
        return False, str(e)

def _ensure_ollama_running(timeout=None):
    timeout = timeout or 10  # Default timeout if not provided
    # If there is already a listener, OK
    if _is_ollama_listening():
        return True, None
    # Try to start
    started, err = _start_ollama()
    if not started:
        return False, "could not start ollama: {}".format(err)
    # Wait until it responds or the timeout expires
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _is_ollama_listening():
            return True, None
        time.sleep(0.5)
    return False, "timeout waiting for ollama to start"

def generate_with_ollama(prompt, timeout=20):
    # Ensure the service is active before making the request
    ok, err = _ensure_ollama_running()
    if not ok:
        return "[Error: {}]".format(err)

    # Combine with hidden prompt before making the request
    combined_prompt = _merge_hidden_prompt(prompt)

    payload = {
        "model": MODEL_NAME,
        "prompt": combined_prompt,
        "stream": False
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        if resp.status_code == 404:
            return "[Error: The requested model is not available in Ollama or the endpoint does not exist. Ensure that the model 'gemma3:1b' is loaded and available.]"
        resp.raise_for_status()
        data = resp.json()
        return data.get("response") or data.get("text") or str(data)
    except requests.exceptions.ConnectionError:
        return "[Error: Could not connect to Ollama. Is the server started?]"
    except Exception as e:
        return "[Unexpected error: {}]".format(e)

