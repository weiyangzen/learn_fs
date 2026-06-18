# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/finddata.c

This file discovers the Word data blocks that contain non-text document data.

Key behavior:
- `bAddDataBlocks()` walks a Big Block Depot chain and adds physical ranges to the data block list.
- Handles starting offsets inside the first big block and caps each added range to remaining length.
- Rejects unused or out-of-range depot entries.
- `bGet6DocumentData()` reads Word 6/7 fast-save CLX text-info data, locates type-2 piece tables, and adds the corresponding data ranges.

Important details:
- Uses header offsets `0x160` and `0x164` for Word 6/7 CLX location and length.
- Reads CLX content through `bReadBuffer()` over the document block chain.
- The parser skips type-0/type-1 records and expects type 2 for piece data.

Filesystem relevance:
- Direct: follows Word block allocation chains and maps logical data streams to physical file offsets.
