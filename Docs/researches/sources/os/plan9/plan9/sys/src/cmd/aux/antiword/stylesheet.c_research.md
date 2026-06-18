# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/stylesheet.c

This file builds the stylesheet arrays used as defaults for paragraph and character formatting.

Key behavior:
- Stores style and font defaults in parallel arrays indexed by stylesheet records.
- Implements built-in WinWord 1/2 style/font defaults and `stc` to `istd` conversion.
- Parses WinWord 1/2, Word 6/7, and Word 8 stylesheet formats.
- Resolves base-style inheritance by repeatedly filling records whose base style is already known.
- Supplies `vFillStyleFromStylesheet()` and `vFillFontFromStylesheet()` to initialize run-level formatting.

Important details:
- Word 8 stylesheet names are Unicode and lengths are converted from characters to bytes.
- Unresolved or empty records fall back to default style/font data.
- Word 6/7 and Word 8 share similar STD/UPX parsing but differ in table stream/block access and name encoding.

Filesystem relevance:
- Indirect: reads stylesheet records from Word file streams and feeds rendering metadata.
