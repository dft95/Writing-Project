# Project Plan: Story Bible + Writing Assistant

## What this is

A tool that ingests a book's source material (docx, pdf, notes, outlines —
whatever format the worldbuilding lives in) and builds an internal knowledge
store from it. A chat interface lets the user:

1. Ask questions about the story, answered from the ingested material (not
   general knowledge).
2. Request generated excerpts/scenes that stay consistent with established
   canon.

First target project: *Warrior*. Should generalize to any book, not be
hardcoded to one.

## Phased approach

### Phase 1 — MVP (no vector DB, no embeddings)

A single novel's drafts + notes typically fit within Claude's context
window, so skip retrieval infrastructure for now.

- Script to extract text from docx/pdf/etc into plain markdown files in the
  repo.
- Simple chat script or webpage that stuffs the ingested text as context
  alongside the user's question and calls the Claude API.
- Goal: get the ingest -> ask -> answer/generate loop working end to end.

### Phase 2 — Structured story bible

- Have Claude do an extraction pass over the ingested text to produce a
  structured knowledge file (characters, locations, timeline,
  relationships) as JSON/markdown.
- Use this for faster lookups and consistency checking (e.g. flag
  contradictions like inconsistent eye color).

### Phase 3 — Real RAG (only if needed)

- If the corpus outgrows the context window (multiple books, huge notes),
  chunk + embed the text and retrieve relevant chunks per query instead of
  passing everything.
- Don't build this until Phase 1/2 prove insufficient.

## Stack

- Python for ingestion (`python-docx`, `pdfplumber`).
- Claude API for Q&A and writing generation.
- Small local web app (e.g. FastAPI + minimal frontend) for the chat
  interface rather than a CLI, since it needs to be usable from a phone
  too.

## Status

Not yet started — this doc captures the agreed direction before
implementation begins. Reorganize files into their proper structure once
Phase 1 is underway.
