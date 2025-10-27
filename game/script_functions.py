def split_into_blocks(text, limit=32):
    """
    Splits the text into consecutive blocks of up to 'limit' words.
    Intermediate blocks end with '...' to indicate continuation.
    """
    words = text.split()
    blocks = []
    for i in range(0, len(words), limit):
        block = words[i:i+limit]
        if i + limit < len(words):
            blocks.append(" ".join(block) + "...")
        else:
            blocks.append(" ".join(block))
    return blocks