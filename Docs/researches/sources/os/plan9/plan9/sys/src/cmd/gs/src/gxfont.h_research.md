# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont.h

## Purpose
Defines Ghostscript's core font object model, font information records, glyph information records, and font procedure vector.

## Main Types
- `gs_font_info_t`: font-level metrics and descriptor-like fields, including PDF FontDescriptor-compatible values plus names/copyright strings.
- `gs_glyph_info_t`: glyph-level width, bbox, composite-piece, vertical-vector, and outline-width information.
- `gs_font_procs`: virtual procedure table for font definition, scaling, encoding, glyph enumeration, glyph metrics, outlines, glyph names, and text rendering.
- `gs_font`: base generic font object with memory, directory, notify list, matrix, type, bitmap behavior, WMode, PaintType, StrokeWidth, names, and procedures.
- `gs_font_base`: non-composite base font with FontBBox, UID, FAPI hooks, and encoding indexes.

## Key Procedure Groups
- Font-level: `define_font`, `make_font`, `font_info`, `same_font`.
- Glyph-level: `encode_char`, `decode_glyph`, `enumerate_glyph`, `glyph_info`, `glyph_outline`, `glyph_name`.
- Rendering-level: `init_fstack`, `next_char_glyph`, `build_char`.

## Important Contracts
- `glyph_info` implementers must derive WMode from requested flags, not from `font->WMode`, because descendant fonts can inherit WMode.
- `glyph_outline` similarly receives explicit WMode.
- Subclasses of `gs_font` must use `gs_font_finalize`.
- Font names are fixed-size `gs_font_name` records used for font directory and high-level output lookup.

## Declared Helpers
- Font allocation and notification helpers.
- Default/no-op procedure declarations.
- `gs_font_glyph_is_notdef`.
- `gs_font_parent`.
- `gx_extendeg_glyph_name_separator`, used by PDF width/metrics glyph-name conflict logic and copied-font cleanup.

## Integration
This is the central dependency for `gxfcopy.c`, Type 0/1/42 font headers, text rendering, font cache, and high-level output.
