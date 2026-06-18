# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/blocklist.c

Antiword text-block list manager. It records physical file offsets, logical character positions, lengths, Unicode flags, and property modifiers for Word document text streams.

Important behavior:
- Maintains separate linked lists for main text, footnotes, headers/footers, macros, annotations, endnotes, text boxes, and header text boxes.
- `bAdd2TextBlockList()` validates and appends/merges contiguous blocks with matching encoding and property modifier.
- `vSplitBlockList()` splits the initially collected text list into logical sublists based on Word character counts, optionally extending intermediate block lengths to big-block boundaries.
- Empty text box lists are detected by reading actual bytes and discarded.
- `usNextChar()` streams characters from selected lists, reading backing file data in `BIG_BLOCK_SIZE` chunks and combining Unicode bytes when needed.
- `ulCharPos2FileOffsetX()`, `ulCharPos2FileOffset()`, `ulHdrFtrOffset2CharPos()`, and `ulGetSeqNumber()` translate between logical character positions and physical file offsets.

Filesystem relevance:
- Core mapping layer between fragmented Word/OLE stream storage and logical text iteration.
