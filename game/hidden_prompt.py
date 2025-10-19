import os

HIDDEN_PROMPT_FILE = "hidden_prompt.txt"
DEFAULT_HIDDEN_PROMPT = """You are an expert role-play facilitator. 
Adopt and maintain a coherent personality based on the user's request. 
Use present tense, sensory details, and concrete actions to enhance immersion. 
Ask clarifying questions when necessary and adapt the tone to the given context.
Your name is Clara"""

def _hidden_prompt_path(filename=None):
    base = os.path.dirname(__file__) or os.getcwd()
    return os.path.join(base, filename or HIDDEN_PROMPT_FILE)

def load_hidden_prompt(filename=None):
    """
    Reads the hidden prompt from a .txt file in the same directory as the module.
    Returns DEFAULT_HIDDEN_PROMPT if the file does not exist or an error occurs.
    """
    path = _hidden_prompt_path(filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content if content else DEFAULT_HIDDEN_PROMPT
    except Exception:
        return DEFAULT_HIDDEN_PROMPT

def save_hidden_prompt(text, filename=None):
    """
    Saves/updates the hidden prompt in the .txt file.
    Returns (True, None) on success or (False, error_message) on failure.
    """
    path = _hidden_prompt_path(filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text or "")
        return True, None
    except Exception as e:
        return False, str(e)

def _merge_hidden_prompt(user_prompt):
    """
    Combines the hidden prompt with the user's prompt.
    The hidden prompt is placed at the beginning, separated by a clear divider.
    """
    hidden = load_hidden_prompt()
    if not hidden:
        return user_prompt or ""
    if not (user_prompt and user_prompt.strip()):
        return hidden.strip()
    return hidden.strip() + "\n\n---\n\nUsuario:\n" + user_prompt.strip()
