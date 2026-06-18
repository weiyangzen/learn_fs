# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fonts_r.c

RISC OS-specific font implementation.

Key behavior:

- `pOpenFontTableFile()` opens `<AntiWord$FontNamesFile>` or creates it by copying `<AntiWord$Dir>.Resources.Default` into the configured save location.
- `vCloseFont()` releases the current RISC OS font handle using `Font_LoseFont`.
- `tOpenFont()` maps Word font/style through the generic font table, then opens a RISC OS font with `Font_FindFont`; returns a drawfile font reference of `iFontnumber + 1`.
- `tOpenTableFont()` resolves `TABLE_FONT` and opens it.
- `lComputeStringWidth()` uses RISC OS `Font_StringWidth`; if no font is open or an error occurs, falls back to character-count millipoints.
- `tCountColumns()` and `tGetCharacterLength()` are one-byte assumptions for this platform.

This file owns live RISC OS font handles and uses DeskLib/RISC OS APIs. It is the platform counterpart to `fonts_u.c`.
