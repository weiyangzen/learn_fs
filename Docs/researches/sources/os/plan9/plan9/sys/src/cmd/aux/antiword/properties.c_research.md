# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/properties.c

This file dispatches property extraction according to detected Word version.

Key behavior:
- `vGetPropertyInfo()` calls the version-specific stylesheet, document, section, paragraph, header/footer, character, font table, and summary readers.
- Skips expensive character/font/image-oriented parsing for output modes that do not need it.
- Handles Word for DOS, WinWord 1/2, Word 6/7, and Word 8; Word 4/5 has no active property extraction path here.
- `ePropMod2RowInfo()` resolves stored property modifiers and delegates row detection to the appropriate version parser.

Important details:
- The Word 8 path reads list information before stylesheet and paragraph data so list-dependent style data can be resolved.
- Font table correction is always run after property extraction.

Filesystem relevance:
- Indirect: coordinates parsing of file-resident Word metadata and OLE substreams.
