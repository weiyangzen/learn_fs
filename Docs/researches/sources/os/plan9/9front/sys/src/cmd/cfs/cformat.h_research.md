# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/cformat.h

On-disk format definitions for the Plan 9 caching filesystem.

Key definitions:
- Allocation and inode magic values: `Amagic`, `Imagic`.
- `Indbno` marks indirect pointer blocks; `Notabno` marks absent blocks.
- `Dalloc` allocation blocks contain header metadata and bitmaps.
- `Dptr` records file block number, disk block number, and valid byte range within the block.
- `Inode` records qid, cached length, root data pointer, and in-use flag.
- `Dinode` inode blocks contain header metadata plus inode array.

Dependencies:
- Uses Plan 9 `Qid` and integer types through including files.

Research notes:
- The cache stores sparse byte ranges, not necessarily complete file blocks.
