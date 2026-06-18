# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/string.c

Draws and measures strings using memory subfonts.

Key functions:
- `memimagestring`: decodes UTF-8 runes, looks up `Fontchar` metrics, and draws glyph masks from `f->bits` with `memdraw`.
- `memsubfontwidth`: returns width and height for a string in a subfont.

Important behavior:
- Skips runes outside the subfont range.
- Source color point advances by glyph width to keep patterned colors aligned.
