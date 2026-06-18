# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fmt_text.c

This file implements Antiword’s “formatted text” output backend.

Key behavior:
- Initializes output encoding and diagram cursor state.
- Emits UTF-8 strings unchanged when UTF-8 output is selected.
- For non-UTF-8 output, preserves leading/trailing spaces, converts non-breaking spaces to normal spaces, and wraps visible text in simple style markers: `*bold*`, `/italic/`, and `_underline_`.
- Moves horizontally by emitting filler characters when the current diagram X/Y position changes.
- Advances the diagram cursor by the supplied string width after each substring.

Important details:
- Lazily resolves the local non-breaking-space byte through `ucGetNbspCharacter()`.
- Style markers exclude surrounding whitespace so spaces remain outside emphasis delimiters.
- Depends on diagram positioning fields even though output is textual.

Filesystem relevance:
- Indirect: output formatting layer for text extracted from Word document storage.
