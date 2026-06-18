# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fonts_u.c

Unix font implementation, including Plan 9 build paths via `antiword.h` platform macros.

Key state:

- `bUsePlainText`: true for plain text/XML-like output where font metrics are unnecessary.
- `eEncoding`: current output encoding.

Key functions:

- `pOpenFontTableFile()` searches for `fontnames` in:
  - `ANTIWORDHOME`,
  - user home `.antiword`,
  - `GLOBAL_ANTIWORD_DIR`.
- `vCloseFont()` resets encoding and plain-text mode.
- `tOpenFont()` chooses whether metrics are needed based on conversion type; for PS/PDF/draw it maps Word font/style to one of the 32 generated PostScript font names in `fontinfo.h`.
- `tOpenTableFont()` opens the configured table font.
- `szGetFontname()` returns the generated PostScript font name for a font reference.
- `lComputeStringWidth()`:
  - UTF-8 plain text uses `utf8_strwidth`,
  - plain text uses byte count,
  - Cyrillic uses fixed 600-unit width,
  - Latin-1 uses `ausCharacterWidths1`,
  - Latin-2 uses `ausCharacterWidths2`.
- `tCountColumns()` and `tGetCharacterLength()` switch between byte semantics and UTF-8 helpers.

This is the primary consumer of `fontinfo.h` and the Unix-side bridge between Word font metadata and output positioning.
