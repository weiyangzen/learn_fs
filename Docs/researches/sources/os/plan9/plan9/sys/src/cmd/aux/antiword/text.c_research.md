# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/text.c

This file implements plain text output primitives.

Key behavior:
- Initializes text-output state from conversion options.
- Writes substrings, line moves, paragraph starts/ends, and page ends to the output file.
- Emits UTF-8 strings unchanged, while non-UTF-8 output maps local non-breaking spaces to ordinary spaces.
- Converts horizontal position to filler characters when moving to a new text position.

Important details:
- Paragraph gaps at least `HEADING_GAP` become blank lines.
- `vSubstringTXT()` requires the provided length to match `strlen()`.

Filesystem relevance:
- Direct output writing through `FILE *`, but no filesystem metadata handling.
