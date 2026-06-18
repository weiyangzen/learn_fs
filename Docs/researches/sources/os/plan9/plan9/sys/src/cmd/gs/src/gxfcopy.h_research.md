# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcopy.h

## Purpose
Declares the font-copying API used by high-level output devices and font-subsetting code.

## Public Interface
- `gs_copy_font`: copies a font shell without glyph data.
- `gs_copy_glyph`: copies a glyph and dependent subglyphs into a copied font.
- `gs_copy_glyph_options`: copies with stricter duplicate/new-glyph controls.
- `gs_copied_font_add_encoding`: adds a character-to-glyph encoding entry.
- `gs_copy_font_complete`: copies all glyphs and encoding data.
- `gs_copied_can_copy_glyphs`: checks whether another compatible font can provide glyphs.
- `copied_drop_extension_glyphs`: removes synthetic extension glyphs before embedding.

## Option Flags
- `COPY_GLYPH_NO_OLD`: error if top-level glyph was already copied.
- `COPY_GLYPH_NO_NEW`: error if top-level glyph was not already copied.
- `COPY_GLYPH_BY_INDEX`: interpret glyph as an index/GID where relevant.

## Documented Font Coverage
- Supports Type 1/2, Type 42, CIDFontType 0, and CIDFontType 2.
- Type 1/2 copying preserves Subrs and GlobalSubrs but not OtherSubrs.
- Type 42 copying strips/copies non-glyph TrueType data and copies outlines separately.
- CIDFontType 0 copies Type 1/2 subfonts and subroutines.
- CIDFontType 2 copies glyph data and CIDMap entries incrementally.

## Important Constraints
The header states copied fonts support querying and rendering but not `make_font`. It also warns that compatibility is the caller's responsibility for `gs_copy_glyph`, while `gs_copied_can_copy_glyphs` exists for explicit checking.
