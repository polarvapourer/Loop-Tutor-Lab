# Loop Tutor Lab

I built a small Python experiment to compare how two local AI models teach
a Java loop. The loop reads binary digits from left to right and updates a
running total with `total = total * 2 + bit`.

## How the experiment works

I used `qwen2.5-coder:3b` and `qwen2.5-coder:7b` through Ollama.

1. **Reading round.** Both models explain the same loop. The program displays
   their finished replies as Tutor A and Tutor B. The learner traces a fresh
   input and votes on which explanation was clearer before seeing the names.
2. **Live round.** The learner asks each model for a hint in an Ollama chat.
   Python checks the learner's final answer and reports the elapsed time and
   number of attempts.

## What happened in my first run

I gave the two written explanations a tie for clarity. When I checked the
arithmetic, I found that the 3B model had evaluated `1 * 2 + 0` as `3`.
The 7B model got that step right.

In the live round, I asked both tutors to leave the final total for me.
Both gave it away. The 7B model correctly traced `10110` to `22`.
The 3B model explained the update rule correctly but gave `22` for `11010`,
whose running totals are `1, 3, 6, 13, 26`. It repeated the same wrong
answer when I sent the prompt again in the same chat.

This was one test run, and I had the answer key. I used it to check the
program's behaviour. The timings from this run cannot establish which
model helps a new learner finish faster.

## Run it locally

You need Python 3 and Ollama. The Python script uses the standard library.

1. Start Ollama. Run `ollama list` and check for both model names above.
   If either is missing, run `ollama pull` followed by its model name.
2. Open two terminals in the project folder.
3. In the first terminal, run `py tutor_lab.py` on Windows or
   `python3 tutor_lab.py` on macOS or Linux.
4. Follow the reading-round prompts. During the live round, use the second
   terminal for the `ollama run` command printed by the program. Enter your
   numerical answers in the first terminal.

The script sends the reading prompt to Ollama on `127.0.0.1:11434`.
It prints the results in the terminal and does not create a results file.

## References

- [Worth the Wait? How Response Time and Streaming Shape Judgments of Generative AI Answers and Chatbot Engagement](https://arxiv.org/abs/2611.33050)
- [Systems-Lab calculator used to check the binary examples](https://polarvapourer.github.io/Systems-Lab/calculator.html)