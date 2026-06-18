# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/depot.c

This file computes physical offsets for OLE big-block and small-block depot indices.

Key behavior:
- Builds a cached list of big blocks that contain the small-block stream.
- Validates Big Block Depot chain indices while walking the chain.
- Converts a big-block index to `(index + 1) * BIG_BLOCK_SIZE`.
- Converts a small-block index through the cached small-block-list mapping and `SMALL_BLOCK_SIZE`.

Important details:
- `SIZE_RATIO` is `BIG_BLOCK_SIZE / SMALL_BLOCK_SIZE`.
- Returns `0` for invalid small-block mappings or unsupported block sizes.
- Big-block offset skips the OLE header block by adding one.

Filesystem relevance:
- Direct: maps OLE compound-document allocation tables to physical file offsets.
