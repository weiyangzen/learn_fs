# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordwin.c

WinWord 1/2 document initializer.

Key responsibilities:
- Reads the 384-byte WinWord header.
- Verifies WinWord 1.x or 2.0 magic/version.
- Rejects fast-saved and encrypted documents.
- Builds one combined text block containing main text, footnotes, headers/footers, macros, and annotations.
- Splits that text block into logical lists.
- Optionally builds a data block for images when output settings require images.
- Invokes property parsing, tab width setup, and notes parsing.

Important behavior:
- Template flag is logged but not rejected.
- Data block extraction is skipped for text-only/XML/no-image modes.
- Image data is approximated as the region between end-of-text and character-info start.

Dependencies:
- Text/data block list APIs, option state, property dispatcher, tab-stop parser, notes parser.

Research relevance:
- Legacy Windows Word entry point into the shared conversion pipeline.
