# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcopy.h

Declares the public API for high-level-output font copying and glyph subsetting.

Key declarations:
- `gs_copy_font` copies a font shell, excluding most glyph definitions.
- `gs_copy_glyph` copies one glyph and any sub-glyphs into a copied font.
- `gs_copy_glyph_options` adds `COPY_GLYPH_NO_OLD`, `COPY_GLYPH_NO_NEW`, and `COPY_GLYPH_BY_INDEX`.
- `gs_copied_font_add_encoding` adds character-to-glyph encoding entries for copied character-indexed fonts.
- `gs_copy_font_complete` copies all glyphs and relevant encoding entries.
- `gs_copied_can_copy_glyphs` checks whether glyphs from another font are compatible with an existing copied font.
- `copied_drop_extension_glyphs` removes synthetic extension glyphs before embedding.

Behavior contract:
- Supports Type 1/2, Type 42, CIDFontType 0, and CIDFontType 2.
- Does not copy PostScript-only data such as Metrics arrays, CDevProc, and full FontInfo beyond `font_info`.
- Destination fonts must come from `gs_copy_font`.
- `gs_copy_glyph` does not itself verify source/destination compatibility.

Dependencies:
- Includes `gsccode.h` and forward-declares `gs_font` and `gs_matrix`.

Research notes:
- The header is the contract for font subsetting used by high-level output devices such as PDF/PS writers.
- The comments are unusually detailed and define the per-FontType limitations that callers must respect.
