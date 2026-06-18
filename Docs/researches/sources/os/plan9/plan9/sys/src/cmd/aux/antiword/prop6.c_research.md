# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop6.c

## Summary
`prop6.c` parses property information for Word 6 and Word 7/95 compound-document streams. It is the Word 6/7 counterpart to `prop2.c`, using Big Block Depot stream reads and newer sprm layouts.

## Main Responsibilities
- Defines `iGet6InfoLength()` for Word 6/7 property stream advancement.
- Reads document properties from the WordDocument stream via `bReadBuffer()`.
- Parses section PLCs, section property pages, outline numbering data, section breaks, columns, and header/footer flags.
- Builds header/footer metadata from PLC character-position tables.
- Detects table rows/cells and extracts borders/column widths from Word 6/7 table sprms.
- Parses paragraph property BTE pages into style records, including list metadata and file-offset conversion.
- Applies character property sprms for revision deletion, plain/default resets, bold/italic/strike/caps/hidden toggles, underline, font number, font size, color, superscript/subscript, and size increments.
- Extracts picture offsets from `fcPic` sprms while filtering OLE objects.

## Key Dependencies
Uses OLE Big Block Depot reads, style/font/row/header/footer/picture list APIs, stylesheet defaults, character-position-to-file-offset conversion, and Word constants.

## Filesystem Relevance
Reads from compound-file streams by depot chain. No kernel or filesystem implementation behavior.

## Notes
There is an apparent debug-only typo near `vGet6ChrInfo()` referencing `lBeginCharInfo` instead of `ulBeginCharInfo`; impact depends on debug macro expansion.
