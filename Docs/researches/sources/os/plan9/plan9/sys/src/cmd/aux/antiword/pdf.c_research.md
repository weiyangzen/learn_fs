# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/pdf.c

## Summary
`pdf.c` is a hand-written PDF 1.3 backend. It emits catalog/pages/info/resources/font objects, tracks file positions for xref generation, manages page flow, and writes text and inline image data.

## Main Responsibilities
- Maintains object numbers, page object arrays, object offsets, stream positions, and xref trailer state.
- Creates document information dictionaries from parsed Word metadata.
- Emits standard Type 1 font resources and Latin-1/Latin-2 encoding differences.
- Handles headers and footers per section/page, including first-page and odd/even variants.
- Moves text positions in PDF text matrices and creates new pages when footer space is reached.
- Emits inline images for JPEG, PNG, DIB, and fallback formats with appropriate filters and color spaces.
- Escapes PDF strings and supports superscript/subscript baseline shifts.

## Key Dependencies
Uses document metadata getters, header/footer lists, output alignment helpers, image metadata, color conversion, font lookup, and ASCII85/image translators.

## Filesystem Relevance
Writes PDF bytes to the output stream and uses `ftell()` to reconcile image byte positions. It does not read filesystem metadata.

## Notes
PDF support explicitly excludes UTF-8 and Cyrillic encodings via option validation and runtime checks.
