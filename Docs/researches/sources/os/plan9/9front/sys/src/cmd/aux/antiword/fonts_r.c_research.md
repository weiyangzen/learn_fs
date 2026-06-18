# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fonts_r.c

This file is the RISC OS font backend.

Key routines:
- `pOpenFontTableFile()` opens `<AntiWord$FontNamesFile>` or creates it from bundled defaults using RISC OS environment paths.
- `vCloseFont()` releases the current RISC OS font handle.
- `tOpenFont(...)` maps Word font/style to antiword’s font table, opens the RISC OS font via `Font_FindFont`, and returns a drawfile font reference.
- `tOpenTableFont(...)` opens the configured table font.
- `lComputeStringWidth(...)` uses `Font_StringWidth` when a font is active, otherwise falls back to character-count width.
- `tCountColumns(...)` and `tGetCharacterLength(...)` are one-byte/one-column implementations.

Important behavior:
- Stores one global current font handle, initialized to invalid.
- Font open failures return font reference zero and may report RISC OS error details.
- Control table separator has zero width to avoid font subsystem issues.

Dependencies:
- DeskLib/RISC OS `Font` API, drawfile types, filetype/directory helpers, generic font table functions.

Role in antiword:
- Provides native RISC OS font opening and measurement for drawfile-oriented rendering.
