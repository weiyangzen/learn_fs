# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/tabstop.c

Reads the document default tab width.

Key responsibilities:
- Defaults tab width to half an inch in millipoints.
- Reads `dxaTab` from Word for DOS headers, WinWord 1/2 DOP data, Word 6/7 DOP data, or Word 8 table-stream DOP data.
- Selects small or big block depot for Word 8 table stream reads.
- Dispatches by Word version in `vSetDefaultTabWidth()`.

Important behavior:
- Zero `dxaTab` falls back to half an inch.
- Word 4/5 paths leave the default unchanged.
- `lGetDefaultTabWidth()` is present but compiled out under `#if 0`; another implementation may be supplied elsewhere.

Dependencies:
- DOP offsets in version-specific FIB headers, block readers, twips-to-millipoints conversion.

Research relevance:
- Supplies tab expansion width to the text rendering state machine.
