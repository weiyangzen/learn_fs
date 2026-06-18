# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/pdf.c

Handwritten PDF 1.3 backend for Antiword text, pages, fonts, metadata, headers/footers, and inline images.

Key responsibilities:
- Tracks PDF object numbers, xref locations, page objects, stream lengths, current page, section, font, color, and cursor position.
- Writes catalog, info dictionary, pages tree, resources, font objects, encoding differences, xref table, and trailer.
- Supports Latin-1 and Latin-2 font encodings; rejects UTF-8 and Cyrillic PDF output.
- Renders headers and footers through existing output-run alignment logic while avoiding recursive page breaks in footer space.
- Emits text objects with font/color switching, PDF string escaping, octal high-byte escaping, and sub/superscript text rise.
- Embeds JPEG, PNG, and DIB image data as inline images with ASCII85 plus DCT/Flate/DecodeParms as appropriate.
- Adds dummy image rectangles when full image output is unavailable.

Dependencies:
- Uses Antiword metadata getters, font tables, header/footer lists, image metadata, geometry conversion helpers, and `vAlign2Window`.

Notable risks:
- PDF state is entirely static/global and not reentrant.
- File position accounting uses `vfprintf()` return values and resets via `ftell()` after raw image bytes.
- Metadata strings are inserted into PDF literal strings without full PDF escaping beyond the text-output path.
