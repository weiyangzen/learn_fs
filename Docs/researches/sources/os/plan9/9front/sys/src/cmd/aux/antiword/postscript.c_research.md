# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/postscript.c

Handwritten PostScript backend for paginated Antiword output, fonts, text styling, headers/footers, and embedded images.

Key responsibilities:
- Tracks page geometry, landscape mode, encoding, image level, current font/color/position, page count, image count, section index, and first-page state.
- Writes DSC header fields, page setup, prologue functions, encoding redefinitions, document font list, pages, trailer, and EOF.
- Supports Latin-1, Latin-2, and Cyrillic PostScript re-encoding; rejects UTF-8.
- Handles header/footer rendering and page transitions with footer-space recursion protection.
- Emits text with PostScript string escaping, octal high-byte escaping, underline/strike rendering via `LineShow`, and sub/superscript movement.
- Emits EPS-wrapped JPEG/PNG/DIB image streams using ASCII85, DCT/Flate/PNGPredictor filters, color spaces, palettes, and decode arrays.
- Provides dummy image rectangles for unavailable image data.

Dependencies:
- Uses Antiword font tables, metadata, header/footer APIs, image metadata, geometry conversion, style checks, and output alignment.

Notable risks:
- Static global output state prevents concurrent independent PostScript streams.
- EPS/image generation assumes target interpreters support the emitted filters and optional Ghostscript PNG predictor path.
- Page count is written at trailer time and depends on correct page transition bookkeeping.
