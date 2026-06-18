# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/depot.c

Antiword helper for OLE big-block/small-block depot offset calculations.

Important behavior:
- Maintains a dynamically allocated list of big-block indices that contain the small-block depot.
- `bCreateSmallBlockList()` follows the Big Block Depot chain from a starting block to build the small-block list, validating indices against depot length.
- `ulDepotOffset()` maps:
  - big block index to file offset as `(index + 1) * BIG_BLOCK_SIZE`;
  - small block index through the small-block depot list to the physical file offset.
- `vDestroySmallBlockList()` frees depot state.

Filesystem relevance:
- Implements block-address translation for OLE compound-document storage, analogous to indirect block/depot traversal.
