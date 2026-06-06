Modern English to Old English (Futhorc) Translator

This tool translates Modern English into Late West Saxon Old English (c. 950 CE) and then converts that text into Anglo-Saxon Futhorc runes.
How It Works

    Translation: It uses a local Large Language Model (via Ollama) to handle the semantic translation into Old English grammar and vocabulary.

    Transliteration: It uses a custom Python script to map the Old English characters to their corresponding Futhorc runes.

    Validation: It verifies the AI's output against the Bosworth-Toller lexicon to ensure historical accuracy and catch "hallucinations."

Prerequisites

    Ollama: Ensure you have Ollama installed and running.

    Model: Pull the qwen3:8b model (recommended for accuracy) by running:

ollama pull qwen3:8b

3.  **Python:** Ensure Python 3.10+ is installed.
4.  **Dependencies:** Install the required library:
    ```bash
    pip install requests

How to Use

    Ensure Ollama is running in the background.

    Navigate to the project folder in your terminal.

    Run the application:
    Bash

    python futhorc.py

4.  Once the dictionary loads, type your sentence and press **Enter**.
5.  Type `exit` or `quit` to close the program.

*Tip: You can also translate a single sentence directly from the command line:*
```bash
python futhorc.py "The king rides to the hall."

Important Things to Know

    Vibe Coding Disclaimer: This project was created through a collaboration between the creator (who has no formal coding background) and three AI models: Anthropic's Claude 3.5 Sonnet, Google's Gemini, and OpenAI's ChatGPT.

    Validation: The "Validation" bar in the output checks your translation against a historical word list. If a word is flagged as suspect, it doesn't always mean the translation is wrong—it might just be a grammatical variation not found in the base dictionary.

    Loanwords: Modern words (like "email" or "internet") for which no Old English equivalent exists are automatically placed in [LOAN: brackets] and transliterated phonetically into runes.

    Hardware: This tool is optimized for modern laptops with at least 6GB of VRAM (e.g., NVIDIA RTX 4050 and up). If generation is slow, ensure no other heavy AI or gaming applications are using your GPU.

License

Feel free to use, modify, and share this code!
