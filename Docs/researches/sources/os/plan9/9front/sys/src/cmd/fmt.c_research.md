# File Research: sources/os/plan9/9front/sys/src/cmd/fmt.c

## Purpose
Formats text into wrapped paragraphs with optional indentation and join behavior.

## Key Elements
Parses `-i`, `-j`, `-l`/`-w`, reads stdin or files, tokenizes lines into `Word` nodes with indentation and beginning-of-line state, preserves paragraph breaks and indent changes, emits tabs/spaces for indentation, wraps at configured width, and inserts two spaces after sentence-ending punctuation unless it looks like a short uppercase abbreviation.

## Dependencies
Uses Plan 9 Bio and UTF length functions.

## Behavior/Risks
`-j` disables joining across original line starts. Blank whitespace-only lines use prior indentation state. Memory for queued words is freed as emitted, but line buffers from `Brdstr` are consumed by pointer adjustment and are not explicitly freed.
