import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from harness.runners import MODEL_CLAUDE, MODEL_OPENAI


def test_anthropic():
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = client.messages.create(
        model=MODEL_CLAUDE,
        max_tokens=20,
        messages=[{"role": "user", "content": "Say hello in 3 words."}],
    )
    print(f"  Claude ({MODEL_CLAUDE}): {resp.content[0].text}")


def test_openai():
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model=MODEL_OPENAI,
        max_tokens=20,
        messages=[{"role": "user", "content": "Say hello in 3 words."}],
    )
    print(f"  OpenAI ({MODEL_OPENAI}): {resp.choices[0].message.content}")


def main():
    print("Testing APIs...")
    for name, fn in [("Anthropic", test_anthropic), ("OpenAI", test_openai)]:
        try:
            fn()
        except Exception as e:
            print(f"  {name} FAILED: {type(e).__name__}: {e}")
    print("Done.")


if __name__ == "__main__":
    main()
