# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont.h

Defines the core Ghostscript font object model, font information structures, glyph information structures, and font procedure vectors.

Key definitions:
- `gs_font_info_t` reports font-level descriptor data such as ascent, bbox, flags, widths, names, copyright, and metrics.
- `gs_glyph_info_t` reports glyph widths, vertical origin, bbox, composite pieces, outline-width distinction, vertical vectors, and CDevProc allowance.
- `gs_font_procs` defines font-level, glyph-level, and glyph-rendering virtual methods.
- Declares default/no-op font procs and `gs_font_procs_default`.
- `gs_font_name` stores short font/key names.
- `gs_font_common` defines base font object fields: links, memory, directory, IDs, base font, matrix, type, bitmap policy, WMode, PaintType, StrokeWidth, procedure vector, key/font names.
- `gs_font` is the generic font object.
- `gs_font_base_common` extends generic fonts with FontBBox, UID, FAPI hooks, and encoding indexes.
- `gs_font_base` is the common base for non-composite fonts.

Key declarations:
- `gs_font_alloc`
- `gs_font_notify_init`
- `gs_font_notify_register`
- `gs_font_notify_unregister`
- `gs_font_base_alloc`
- `gx_extendeg_glyph_name_separator`
- `gs_font_glyph_is_notdef`
- `gs_font_parent`

Dependencies:
- Includes character code, public font, glyph data, matrix, notify, UID, GC struct, and font-type headers.

Research notes:
- This is the central internal font ABI used by copied fonts, Type 1, Type 42, composite fonts, text rendering, and high-level output.
- Comments emphasize that `glyph_info`/`glyph_outline` implementations must derive WMode from arguments rather than reading `font->WMode` for descendant fonts.
