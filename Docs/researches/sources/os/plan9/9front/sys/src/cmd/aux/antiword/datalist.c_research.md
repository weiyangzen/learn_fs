# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/datalist.c

Antiword data-block list manager. It tracks fragmented physical file ranges that form a logical data stream and provides sequential/endian-aware readers.

Important behavior:
- `bAdd2DataBlockList()` validates data blocks and merges contiguous physical/logical ranges.
- `bSetDataOffset()` positions the logical data cursor at a specific physical file offset and preloads the current block cache.
- `iNextByte()` streams bytes across block boundaries, loading up to `BIG_BLOCK_SIZE` at a time.
- `usNextWord()`, `ulNextLong()`, `usNextWordBE()`, and `ulNextLongBE()` read little- and big-endian integers.
- `tSkipBytes()` advances across cached and subsequent blocks.
- `ulDataPos2FileOffset()` maps logical data position back to physical file offset.

Filesystem relevance:
- Abstracts fragmented compound-document storage into stream-like reads, matching filesystem block-list behavior.
