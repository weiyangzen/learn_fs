# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fmt_text.c

This file implements antiword’s formatted-text output mode.

Key routines:
- `vPrologueFMT(...)` initializes formatted-text output state and diagram coordinates.
- `vPrintFMT(...)` emits a string, preserving leading/trailing spaces while wrapping non-space content in simple markers for bold (`*`), italic (`/`), and underline (`_`).
- `vMoveTo(...)` emits filler characters to simulate horizontal positioning when the vertical position changes.
- `vSubstringFMT(...)` outputs a substring and advances the diagram x-position by the supplied rendered width.

Important behavior:
- UTF-8 output bypasses style-marker insertion and writes bytes directly.
- Non-breaking spaces are converted to ordinary spaces for non-UTF-8 formatted text.
- Style markers are only applied around the non-space core, so surrounding whitespace remains unstyled.

Dependencies:
- Font style predicates, encoding options, draw-unit-to-character conversion, and diagram output state from `antiword.h`.

Role in antiword:
- Provides a lightweight markup-like text rendering backend distinct from plain text, PostScript/PDF, XML, and draw output.
