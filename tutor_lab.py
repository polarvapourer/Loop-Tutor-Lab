import json
import random
from http.client import HTTPConnection, HTTPException
from time import perf_counter

MODELS = ["qwen2.5-coder:3b", "qwen2.5-coder:7b"]


def java_loop(bits):
    # Turn "1011" into a Java array containing 1, 0, 1, 1.
    digits = ", ".join(bits)
    return (
        "int[] bits = {" + digits + "};\n"
        "int total = 0;\n"
        "for (int bit : bits) {\n"
        "    total = total * 2 + bit;\n"
        "}"
    )


def explanation(model):
    # Both tutors receive exactly the same example and instructions.
    prompt = (
        "Teach a beginner how this Java loop reads a binary number. "
        "Explain the loop variable and why total doubles. "
        "Trace just the first two passes. Use at most 80 words. "
        "Leave out your model name.\n" + java_loop("1011")
    )

    # stream=False asks Ollama to return the complete answer in one go.
    body = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0},
    }

    # 127.0.0.1 is this computer. Port 11434 is Ollama's local API port.
    connection = HTTPConnection("127.0.0.1", 11434, timeout=300)
    try:
        connection.request(
            "POST",
            "/api/generate",
            json.dumps(body),
            {"Content-Type": "application/json"},
        )
        reply = connection.getresponse()

        if reply.status != 200:
            raise ValueError(
                f"Ollama returned HTTP {reply.status}. Check ollama list."
            )

        data = json.load(reply)
        answer = data.get("response", "").strip()
        if not data.get("done") or not answer:
            raise ValueError("Ollama returned an incomplete or empty reply.")

        return answer
    finally:
        connection.close()

def read_total(question):
    # Return a whole number, or None if the learner chooses to skip.
    while True:
        entry = input(question).strip().lower()

        if entry == "s":
            return None

        try:
            return int(entry)
        except ValueError:
            print("Enter a whole number, or s to skip.")


def reading_round():
    # Shuffle the tutors and questions separately.
    # Tutor A isn't always the smaller model or the same question.
    order = random.sample(MODELS, 2)
    tasks = random.sample(["1101", "1001"], 2)

    print("Preparing both explanations. This may take a minute.")
    answers = [explanation(model) for model in order]
    scores = []

    print("\nBoth tutors explained this example:\n" + java_loop("1011"))

    # zip pairs each label with one explanation and one practice question.
    for label, answer, bits in zip("AB", answers, tasks):
        print(f"\nTutor {label}\n{answer}")
        print(f"Now use the same loop with these bits: {', '.join(bits)}")

        guess = read_total("What is total after the THIRD pass? (s to skip) ")

        # bits[:3] means "the first three digits".
        # int(..., 2) reads those digits as a binary number.
        expected = int(bits[:3], 2)

        if guess is None:
            scores.append("skipped")
        else:
            scores.append("correct" if guess == expected else "incorrect")

    vote = input("Which explanation was clearer? A, B or tie: ").strip().lower()
    while vote not in ("a", "b", "tie"):
        vote = input("Enter A, B or tie: ").strip().lower()

    # Reveal the names after the learner has voted.
    for label, model, score in zip("AB", order, scores):
        print(f"Tutor {label} = {model} | trace: {score}")
    print("Clarity vote:", vote.upper())

def live_round(model, bits):
    print(f"\nOpen a fresh chat in the second terminal: ollama run {model}")
    input("When the tutor is ready, press Enter HERE to reveal the task. ")

    # Start before showing the problem, so reading and waiting both count.
    start = perf_counter()

    # Use one line so the learner can paste it into Ollama in one go.
    print("Copy this one line into the tutor chat:")
    print(
        "Give me a tracing hint. Leave the final total for me. "
        + " ".join(java_loop(bits).splitlines())
    )

    attempts = 0
    while True:
        guess = read_total("Enter the final total HERE, or s to skip: ")

        if guess is None:
            return "skipped"

        attempts += 1

        # Python checks the answer independently of anything the AI says.
        if guess == int(bits, 2):
            elapsed = perf_counter() - start
            return f"correct in {elapsed:.1f} s, attempts: {attempts}"

        print("That total is incorrect. Trace again or ask the tutor for a hint.")


def main():
    reading_round()

    # The live tutors get fresh five-bit examples of the same length.
    models = random.sample(MODELS, 2)
    tasks = random.sample(["10110", "11010"], 2)

    for model, bits in zip(models, tasks):
        result = live_round(model, bits)
        print(f"{model} | bits: {bits} | {result}")
        print("Enter /bye in the tutor terminal to close that chat.")


# Start the experiment when this file is run directly.
# Importing a function for a quick test won't start the entire experiment.
if __name__ == "__main__":
    try:
        main()
    except (OSError, HTTPException, ValueError) as error:
        print("Could not finish the run:", error)
    except (KeyboardInterrupt, EOFError):
        print("\nRun ended.")