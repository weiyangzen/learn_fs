# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxxfont.h

Defines Ghostscript’s external-font object interface.

Key points:
- Documents design assumptions: devices supply xfonts, xfonts are transformation-specific objects, and they provide bitmaps independent of a particular device.
- Defines `gx_xfont_common`, `gx_xfont`, and `gx_xfont_procs`.
- Procedure vector covers lookup, character/glyph mapping, metrics, rendering, and release.
- `lookup_font` is explicitly a factory callback taking a device, font name, encoding, UID, matrix, and allocator.
- `render_char` can target any Ghostscript device.
- Provides GC descriptor helper macros for xfonts that hold a single device pointer.

Research notes:
- This is a device-facing font acceleration/bitmap interface.
- The header preserves compatibility history around deprecated and later restored glyph mapping behavior.
