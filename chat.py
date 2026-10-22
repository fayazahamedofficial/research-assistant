from src.llm import stream

SYSTEM = "You are a helpful, concise assistant."
history = []

while True:
    user_input = input("\nYou: ").strip()
    if user_input.lower() in ("quit", "exit"):
        break
    if not user_input:
        continue

    history.append({"role": "user", "content": user_input})

    print("\nAI: ", end="", flush=True)
    reply = ""
    for piece in stream(history, system=SYSTEM):
        print(piece, end="", flush=True)
        reply += piece
    print()

    history.append({"role": "assistant", "content": reply})