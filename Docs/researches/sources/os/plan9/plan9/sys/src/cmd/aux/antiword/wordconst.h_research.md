# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordconst.h

This header defines core constants and macros for Word parsing and output conversion.

Key contents:
- OLE/Word block sizes, small-vs-big stream threshold, invalid offsets, max columns/tabs, font sizes, font style bits, colors, list types, alignment values, and table border flags.
- Little-endian and big-endian byte extraction macros.
- Unit conversion macros for twips, millipoints, draw units, points, and character cells.
- Word control characters, pseudo note characters, Unicode constants, and platform-local fallback glyphs.

Important details:
- The constants establish the shared interpretation contract for nearly every parser in this group.
- `FC_INVALID`, `CP_INVALID`, `END_OF_CHAIN`, and block-size constants are especially important for OLE stream traversal.

Filesystem relevance:
- Indirect but foundational: defines block/container constants used by Word/OLE file readers.
