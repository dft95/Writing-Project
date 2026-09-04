"""Chat with your story, grounded in ingested source material.

Usage:
    python chat.py [--context <dir>] [--model <model>]

Requires ANTHROPIC_API_KEY to be set in the environment. Run ingest.py
first to populate the context directory.
"""

import argparse
import os
from pathlib import Path

SYSTEM_PROMPT_TEMPLATE = """You are a research and writing assistant for a novel. \
Answer questions about the story using ONLY the story material provided below \
as context. If asked to write an excerpt or scene, keep it consistent with \
the established characters, world, and plot in that material. If the \
material doesn't cover something, say so rather than inventing facts \
presented as canon.

--- STORY MATERIAL START ---
{context}
--- STORY MATERIAL END ---
"""


def load_context(context_dir: Path) -> str:
    parts = []
    for path in sorted(context_dir.rglob("*.md")):
        parts.append(f"### {path.relative_to(context_dir)}\n\n{path.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--context", type=Path, default=Path("ingested"), help="Folder of ingested markdown (default: ingested/)"
    )
    parser.add_argument("--model", default="claude-sonnet-5", help="Model to use")
    args = parser.parse_args()

    if not args.context.is_dir():
        raise SystemExit(f"Context directory not found: {args.context}. Run ingest.py first.")

    context = load_context(args.context)
    if not context.strip():
        raise SystemExit(f"No markdown files found in {args.context}/. Run ingest.py first.")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Set ANTHROPIC_API_KEY in your environment before running this.")

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context)

    print(f"Loaded story context from {args.context}/. Ask a question or request an excerpt (Ctrl+C to quit).\n")

    history = []
    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})

        response = client.messages.create(
            model=args.model,
            max_tokens=2048,
            system=system_prompt,
            messages=history,
        )

        reply = "".join(block.text for block in response.content if block.type == "text")
        print(f"\n{reply}\n")
        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
