# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zbfont.c

Provides common font construction utilities and the Type 3 `.buildfont3` operator.

Key behavior:
- `.buildfont3` validates a font dictionary, extracts `BuildChar`/`BuildGlyph`, builds a user-defined base font, and registers it.
- `zfont_encode_char` maps character codes through `Encoding`; for non-conforming Type 3 fonts with `.notdef`, it may synthesize glyph names for high-level devices.
- `zfont_glyph_name` resolves normal glyph names or fabricates numeric names for CID glyphs.
- `gs_font_map_glyph_to_unicode` maps glyphs through `FontInfo/GlyphNames2Unicode` and fallback Unicode decoding resources.
- `build_gs_primitive_font`, `build_gs_outline_font`, `build_gs_simple_font`, `build_gs_font`, and `build_gs_sub_font` fill Ghostscript `gs_font` structures from PostScript dictionaries.
- Handles `CharStrings`, `FontBBox`, UID validation, `PaintType`, `StrokeWidth`, `Encoding`, bitmap width policy, `WMode`, `FID`, `FontMatrix`, aliases, and original font names.
- `lookup_gs_simple_font_encoding` compares a font encoding with known built-in encodings and records exact/nearest matches.

Dependencies and coupling:
- Central bridge between interpreter dictionaries/refs and graphics-library font objects.
- Shares `font_data` refs with character rendering modules (`zchar*.c`).
- Uses VM spaces carefully when allocating font data and when storing dictionary refs.
