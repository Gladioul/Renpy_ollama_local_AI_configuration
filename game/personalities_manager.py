import json
import os

# Almacenamiento en un fichero JSON en la carpeta del módulo
_STORE_FILENAME = "personalities.json"

def _store_path():
    return os.path.join(os.path.dirname(__file__), _STORE_FILENAME)

def _load_store():
    path = _store_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}

def _save_store(store):
    path = _store_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)

def save_personality(label, prompt):
    """
    Guarda/actualiza una personalidad con 'label' y el texto 'prompt'.
    """
    if not label:
        raise ValueError("Label vacío")
    store = _load_store()
    store[str(label)] = str(prompt)
    _save_store(store)

def load_personality(label):
    """
    Devuelve el prompt asociado a 'label' o lanza KeyError si no existe.
    """
    store = _load_store()
    key = str(label)
    if key not in store:
        raise KeyError("No existe la personalidad '{}'".format(label))
    return store[key]

def list_personalities():
    """
    Devuelve la lista de etiquetas guardadas (ordenada).
    """
    store = _load_store()
    return sorted(list(store.keys()))

def delete_personality(label):
    """
    Borra una personalidad. No falla si no existe.
    """
    store = _load_store()
    key = str(label)
    if key in store:
        del store[key]
        _save_store(store)