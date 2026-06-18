# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/finddata.c

This file builds data-block mappings for MS Word document data, especially Word 6/7 fast-save piece data.

Key routines:
- `bAddDataBlocks(...)` walks a Word OLE big-block chain from `ulStartBlock`, skips to the requested logical data offset, and appends `data_block_type` records through `bAdd2DataBlockList`.
- `bGet6DocumentData(...)` reads the Word 6/7 CLX/text-info area from header offsets `0x160`/`0x164`, parses fast-save records, and calls `bAddDataBlocks` for each type-2 piece.

Important behavior:
- Uses `BIG_BLOCK_SIZE` and BBD chain entries to translate logical document offsets into file offsets.
- Rejects invalid BBD indexes, `UNUSED_BLOCK`, damaged chains, null inputs, and lengths beyond `LONG_MAX`.
- Word 6/7 fast-save parsing recognizes record types `0`, `1`, and `2`; unknown types are fatal for this parse path.

Dependencies:
- `antiword.h` supplies types, constants, allocation helpers, endian helpers, list insertion, debug/fail macros, and `bReadBuffer`.

Role in antiword:
- Supplies non-text data block discovery for older Word files, parallel to `findtext.c` text block discovery.
