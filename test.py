# from llm import ask, ask_ollama

# print(ask("gemini", "Say hi"))   # Google, cloud
# print(ask("groq", "Say hi"))     # Groq, cloud
# print(ask_ollama("Say hi"))      # Llama, running on your machine
# test_each.py
from llm import ask, ask_ollama

for name in ["gemini", "groq"]:
    try:
        print(name, "->", ask(name, "Say hi"))
    except Exception as e:
        # Print only the short error, not the whole traceback
        print(name, "FAILED ->", str(e)[:300])

try:
    print("ollama ->", ask_ollama("Say hi"))
except Exception as e:
    print("ollama FAILED ->", str(e)[:300])