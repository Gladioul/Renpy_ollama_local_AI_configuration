import os

HIDDEN_PROMPT_FILE = "hidden_prompt.txt"
DEFAULT_HIDDEN_PROMPT = """You are an expert role-play facilitator. 
Adopt and maintain a coherent personality based on the user's request. 
Use present tense, sensory details, and concrete actions to enhance immersion. 
Ask clarifying questions when necessary and adapt the tone to the given context."""

PERSONALITY_FILE = "personality.txt"
DEFAULT_PERSONALITY = ""

def _hidden_prompt_path(filename=None):
    """
    Returns the absolute path to the hidden prompt or personality file in the same directory as this module.
    """
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

def load_personality(filename=None):
    """
    Reads the personality from a .txt file in the same directory as the module.
    Returns DEFAULT_PERSONALITY if the file does not exist or an error occurs.
    """
    path = _hidden_prompt_path(filename or PERSONALITY_FILE)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content if content else DEFAULT_PERSONALITY
    except Exception:
        return DEFAULT_PERSONALITY

def _merge_hidden_prompt(user_prompt):
    """
    Combines the hidden prompt with the user's prompt.
    The hidden prompt is placed at the beginning, separated by a clear divider.
    If a personality is present, it is also included.
    """
    hidden = load_hidden_prompt()
    personality = load_personality()
    combined_base = hidden.strip()
    if personality and personality.strip():
        combined_base += "\n\n---\n\n" + personality.strip()
    if not combined_base:
        return user_prompt or ""
    if not (user_prompt and user_prompt.strip()):
        return combined_base
    return combined_base + "\n\n---\n\nUsuario:\n" + user_prompt.strip()
