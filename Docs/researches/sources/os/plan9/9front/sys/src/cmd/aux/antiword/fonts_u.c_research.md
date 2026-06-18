# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fonts_u.c

This file is the Unix/DOS/NLM font backend.

Key routines:
- `pOpenFontTableFile()` searches for `fontnames` under `ANTIWORDHOME`, the user home antiword directory, then the global antiword directory.
- `vCloseFont()` resets encoding/font-use state.
- `tOpenFont(...)` decides whether fonts matter for the current conversion type, then maps a Word font/style to an index in `fontinfo.h`.
- `tOpenTableFont(...)` resolves and opens the table font.
- `szGetFontname(...)` returns a PostScript font name by font reference.
- `lComputeStringWidth(...)` computes widths using UTF-8 display width, plain character counts, Cyrillic approximation, or generated Latin-1/Latin-2 metric tables.
- `tCountColumns(...)` and `tGetCharacterLength(...)` use UTF-8 helpers only when UTF-8 encoding is active.

Important behavior:
- Plain text modes avoid font metrics and use character-count widths.
- Draw, PostScript, and PDF modes use font references and generated width tables.
- Cyrillic width support is approximate pending character tables.

Dependencies:
- `fontinfo.h`, option handling, path helpers, UTF-8 helpers, font translation table functions.

Role in antiword:
- Provides portable non-RISC OS font lookup and width measurement for layout and PostScript/PDF output.
