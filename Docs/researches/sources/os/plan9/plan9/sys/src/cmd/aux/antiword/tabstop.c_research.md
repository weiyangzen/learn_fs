# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/tabstop.c

This file determines the document default tab width.

Key behavior:
- Maintains a global default tab width in millipoints.
- Reads `dxaTab` from version-specific document property locations for Word for DOS, WinWord 1/2, Word 6/7, and Word 8.
- Chooses big-block or small-block table access for Word 8 document properties.
- Resets to a half-inch default before each version-specific read.

Important details:
- A zero Word tab width falls back to half an inch.
- The public `lGetDefaultTabWidth()` implementation is compiled out in this file, so the active getter must come from elsewhere or configuration.

Filesystem relevance:
- Indirect: reads document property bytes from file/OLE streams.
