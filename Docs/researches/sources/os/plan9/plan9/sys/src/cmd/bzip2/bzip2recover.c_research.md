# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/bzip2recover.c

Upstream bzip2 1.0 block recovery tool.

It scans a damaged `.bz2` file bit-by-bit looking for bzip2 block headers and end markers, records recoverable block bit ranges, then writes each block into a separate `recNNNN...bz2` file with a synthetic bzip2 header and end marker.

Important pieces:

- `BitStream` abstracts bit-level read/write over `FILE *`.
- `BLOCK_HEADER_*` and `BLOCK_ENDMARK_*` constants detect block boundaries.
- `bStart`, `bEnd`, `rbStart`, `rbEnd` store candidate and recoverable ranges.
- Recovered blocks include the stored block CRC and a new stream wrapper.

The file is explicitly described by upstream as a hacky salvage program, not part of normal compression/decompression.
