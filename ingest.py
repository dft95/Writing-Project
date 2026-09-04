"""Extract text from a folder of source documents into plain markdown files.

Usage:
    python ingest.py <input_dir> [--output <output_dir>]

Supported input types: .docx, .pdf, .txt, .md
"""

import argparse
from pathlib import Path

SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".txt", ".md"}


def extract_docx(path: Path) -> str:
    from docx import Document

    doc = Document(path)
    return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_pdf(path: Path) -> str:
    import pdfplumber

    with pdfplumber.open(path) as pdf:
        return "\n\n".join(page.extract_text() or "" for page in pdf.pages)


def extract_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


EXTRACTORS = {
    ".docx": extract_docx,
    ".pdf": extract_pdf,
    ".txt": extract_text_file,
    ".md": extract_text_file,
}


def ingest(input_dir: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []

    for source_path in sorted(input_dir.rglob("*")):
        if not source_path.is_file() or source_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        extractor = EXTRACTORS[source_path.suffix.lower()]
        text = extractor(source_path).strip()
        if not text:
            continue

        relative = source_path.relative_to(input_dir).with_suffix(".md")
        dest_path = output_dir / relative
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(
            f"<!-- source: {source_path.name} -->\n\n{text}\n", encoding="utf-8"
        )
        written.append(dest_path)

    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path, help="Folder containing source documents")
    parser.add_argument(
        "--output", type=Path, default=Path("ingested"), help="Folder to write extracted markdown (default: ingested/)"
    )
    args = parser.parse_args()

    if not args.input_dir.is_dir():
        raise SystemExit(f"Input directory not found: {args.input_dir}")

    written = ingest(args.input_dir, args.output)

    if not written:
        print("No supported documents found.")
        return

    print(f"Ingested {len(written)} file(s) into {args.output}/:")
    for path in written:
        print(f"  - {path}")


if __name__ == "__main__":
    main()
