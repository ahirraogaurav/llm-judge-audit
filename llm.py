import os                          # read environment variables (API keys)
import requests                    # send HTTP requests (used for Ollama)
from openai import OpenAI          # client that works with any OpenAI-compatible API
from dotenv import load_dotenv     # reads the .env file

# Load keys from .env into environment variables.
# After this line, os.environ["GEMINI_API_KEY"] works.
load_dotenv()

# Lookup table: provider name -> (server URL, key variable name, model name).
# To add a new provider later, add one line here.
PROVIDERS = {
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/",
               "GEMINI_API_KEY", "gemini-flash-latest"),
    "groq":   ("https://api.groq.com/openai/v1",
               "GROQ_API_KEY", "openai/gpt-oss-120b"),
    "gemini2": ("https://generativelanguage.googleapis.com/v1beta/openai/",
                "GEMINI_API_KEY", "gemini-flash-lite-latest"),
    "mistral": ("https://api.mistral.ai/v1",
                "MISTRAL_API_KEY", "mistral-small-latest"),
}


def ask(provider, prompt, system=""):
    """Send one prompt to a cloud model and return its text reply."""

        # Provider names like "ollama:qwen2.5:7b" run on your own machine
    if provider.startswith("ollama:"):
        return ask_ollama(prompt, model=provider.split(":", 1)[1])
    # Unpack the three settings for the chosen provider
    url, key_env, model = PROVIDERS[provider]

    # Connect to that provider using the key from your .env file
    client = OpenAI(base_url=url, api_key=os.environ[key_env])

    # Send the request.
    # temperature=0 -> least random output, so the same input gives
    #   (almost) the same answer. Needed for a fair judge.
    # "system" message sets the model's role/instructions.
    # "user" message is your actual question.
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )

    # The reply is nested inside the response object; pull out just the text
    return response.choices[0].message.content


def ask_ollama(prompt, model="llama3.2:3b"):
    """Send one prompt to the model running locally on your computer."""

    # Ollama runs a small server at localhost:11434 once it's installed.
    # stream=False -> wait for the full reply instead of word-by-word.
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "stream": False,
            "options": {"temperature": 0, "num_ctx": 8192},
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    # .json() converts the raw reply to a Python dict; grab the text
    return response.json()["message"]["content"]