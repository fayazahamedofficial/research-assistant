def chunk_text(text, max_chars=6000, overlap=500):
    """Split text into chunks of about max_chars, cutting between paragraphs.
    Each chunk starts with the tail of the previous one (the overlap)."""

    # Step 1: get a clean list of paragraphs
    paragraphs = []
    for p in text.split("\n"):
        p = p.strip()
        while len(p) > max_chars:       # one giant paragraph: cut it up
            paragraphs.append(p[:max_chars])
            p = p[max_chars:]
        if p:
            paragraphs.append(p)

    # Step 2: pack paragraphs into chunks
    chunks = []
    current = []
    size = 0
    for p in paragraphs:
        if size + len(p) + 1 > max_chars and current:
            chunks.append("\n".join(current))

            # Start the next chunk with the tail of this one (overlap)
            tail = []
            tail_size = 0
            for q in reversed(current):
                if tail_size + len(q) > overlap:
                    break
                tail.insert(0, q)
                tail_size += len(q) + 1
            current = tail
            size = tail_size

        current.append(p)
        size += len(p) + 1

    if current:
        chunks.append("\n".join(current))

    return chunks