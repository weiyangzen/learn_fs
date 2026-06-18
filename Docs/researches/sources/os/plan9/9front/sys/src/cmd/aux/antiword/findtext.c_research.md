# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/findtext.c

This file locates text pieces inside Word document streams and records them as text blocks.

Key routines:
- `bAddTextBlocks(...)` maps character positions and lengths to physical file blocks, accounting for Unicode pieces as two bytes per character.
- `bGet6DocumentText(...)` reads and parses Word 6/7 fast-save CLX data, records property modifiers, and appends text blocks.
- `bGet8DocumentText(...)` reads Word 8/97+ CLX data from the table stream, choosing the small or big block depot based on table stream size.

Important behavior:
- Word 8 piece offsets use bit 30 to distinguish Unicode vs compressed single-byte text; compressed offsets are cleared and divided by two.
- Type-1 CLX records are passed to `vAdd2PropModList`; type-2 records produce piece-table entries.
- Damaged BBD indexes in `bAddTextBlocks` produce a warning/error via `werr`.

Dependencies:
- OLE block-chain readers, piece table endian helpers, text block list insertion, property modifier list handling, and Word document/table PPS metadata.

Role in antiword:
- Central bridge from Word piece-table metadata to ordered text extraction.
