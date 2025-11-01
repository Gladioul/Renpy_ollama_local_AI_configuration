init python:
    """Detecta al inicio del juego si `game/bin` está vacío; si lo está, descarga el instalador de Ollama
    y lo lanza en segundo plano. No bloquea el arranque del juego.
    """
    try:
        import threading, os, subprocess
        try:
            # install_ollama.py está en la carpeta game/ y debe ser importable como módulo simple
            import install_ollama
        except Exception:
            install_ollama = None

        def _install_ollama_if_needed():
            try:
                gamedir = os.path.abspath(renpy.config.gamedir)
                bin_dir = os.path.join(gamedir, "bin")
                # si existe y no está vacío, no hacemos nada
                if os.path.isdir(bin_dir) and any(os.scandir(bin_dir)):
                    renpy.log("Ollama bin not empty; skipping automatic install.")
                    return

                # si no tenemos el helper, solo intentamos descargar el instalador directamente
                url = getattr(install_ollama, 'None', None)
                download_url = None
                if install_ollama is not None:
                    # prefer using the helper (it will place files into bin)
                    try:
                        download_url = os.environ.get('OLLAMA_DOWNLOAD_URL') or "https://ollama.com/download/OllamaSetup.exe"
                        renpy.log(f"Ollama installer: using helper to download {download_url}")
                        install_ollama.ensure_ollama_installed(download_url, bin_dir=bin_dir)
                    except Exception as e:
                        renpy.log("install_ollama helper failed: " + str(e))

                # buscar el instalador .exe dentro de bin y, si se encuentra, lanzarlo (no esperamos a que termine)
                if os.path.isdir(bin_dir):
                    for fn in os.listdir(bin_dir):
                        if fn.lower().endswith('.exe'):
                            installer_path = os.path.join(bin_dir, fn)
                            try:
                                renpy.log('Launching Ollama installer: ' + installer_path)
                                # Ejecutar el instalador en segundo plano. Esto puede elevar permisos según el instalador.
                                subprocess.Popen([installer_path], cwd=bin_dir)
                                return
                            except Exception as e:
                                renpy.log('Failed to launch installer: ' + str(e))
                renpy.log('No installer found in bin after download attempt.')
            except Exception as e:
                renpy.log('Ollama auto-installer thread error: ' + str(e))

        # Iniciar hilo daemon para no bloquear Ren'Py en el init
        t = threading.Thread(target=_install_ollama_if_needed, daemon=True)
        t.start()
    except Exception as e:
        # Registrar pero no detener el inicio del juego
        try:
            renpy.log('Failed to start Ollama install watcher: ' + str(e))
        except Exception:
            pass
