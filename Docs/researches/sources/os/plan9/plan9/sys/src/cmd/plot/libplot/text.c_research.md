# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/text.c

Draws text at the current plot position.

Key responsibilities:
- Parses leading text alignment escapes `\C`, `\R`, `\L`.
- Splits `\n` sequences into multiple displayed lines.
- Converts current plot position to screen coordinates.
- Calls backend `m_text()` and advances current y position for following lines.

Important behavior:
- Default text placement centers the first character at the current point.
- `\R` right-aligns, `\C` centers, and `\L` consumes the marker without special alignment.
- Multiline text updates `copyy` from the backend’s returned screen y coordinate.

Notable risks:
- Relies on backend string sizing behavior; substring sizing in `m_text()` is imperfect.
