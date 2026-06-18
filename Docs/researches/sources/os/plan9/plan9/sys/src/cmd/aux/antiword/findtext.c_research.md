# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/findtext.c

This file discovers the Word file blocks that contain document text.

Key behavior:
- `bAddTextBlocks()` walks a block depot chain and adds logical character ranges as text blocks, accounting for single-byte versus Unicode text.
- `bGet6DocumentText()` reads Word 6/7 fast-save CLX data, records property modifiers, and builds text block ranges from the piece table.
- `bGet8DocumentText()` reads Word 8/97 CLX data from the table stream, choosing small-block or big-block depot based on stream size.
- Decodes Word 8 piece-table offsets, including the `BIT(30)` flag that indicates compressed single-byte text.

Important details:
- Text block file offsets are ultimately resolved relative to the WordDocument stream’s starting block.
- Property modifiers are stored through `vAdd2PropModList()`.
- Word 8 table-stream reading uses either `aulSBD`/`SMALL_BLOCK_SIZE` or `aulBBD`/`BIG_BLOCK_SIZE`.

Filesystem relevance:
- Direct: maps compound-document stream piece tables into physical file offsets for text extraction.
