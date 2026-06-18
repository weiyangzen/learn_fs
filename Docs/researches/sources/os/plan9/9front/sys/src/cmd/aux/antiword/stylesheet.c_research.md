# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/stylesheet.c

Parses Word stylesheet tables into default style and font arrays.

Key responsibilities:
- Stores stylesheet-derived `style_block_type` and `font_block_type` arrays.
- Provides default style/font constructors.
- Maps old WinWord style codes to newer `istd` values.
- Supplies built-in style/font defaults for WinWord 1/2.
- Parses WinWord 1/2 stylesheet records and applies CHPX/PAPX changes.
- Parses Word 6/7 and Word 8 stylesheet `STD`/`UPX` records.
- Resolves base-style dependencies iteratively until no more records can be filled.
- Exposes `vFillStyleFromStylesheet()` and `vFillFontFromStylesheet()` for paragraph/character parsing.

Important behavior:
- Empty or unresolved records are filled with defaults.
- Word 8 style names are Unicode-length based, unlike Word 6/7 byte-length names.
- Paragraph styles can include both paragraph and character UPX data.

Dependencies:
- Version-specific property interpreters (`vGet1FontInfo`, `vGet2FontInfo`, `vGet6StyleInfo`, `vGet8StyleInfo`, etc.), block readers, allocation helpers.

Research relevance:
- Central inheritance/default source for later paragraph and character formatting.
