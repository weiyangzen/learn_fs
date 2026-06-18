# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclmem.h

Defines the RAM-backed command-list file structures and aliases them to the generic clist file API.

Key behavior:
- Sets `MEMFILE_DATA_SIZE` to slightly under 16 KiB to fit allocator size classes efficiently.
- Defines `RAW_BUFFER`, the LRU cached raw decompression buffer.
- Defines `PHYS_MEMFILE_BLK`, the allocated physical data block used for raw or compressed data.
- Defines `LOG_MEMFILE_BLK`, the logical file block that maps file offsets to a physical block and optional raw-cache entry.
- Defines `MEMFILE`, holding allocators, compression eligibility, reserve block chains, logical file position/length, current raw pointer range, compressed physical state, raw-cache list, error code, stream cursors, and compressor/decompressor states.
- Provides a private GC descriptor macro for the `MEMFILE` fields that are GC-managed stream states.
- Maps `memfile_*` operations to the `clist_*` file API names so the RAM implementation satisfies the same interface.
- Declares `clist_compressor_state` and `clist_decompressor_state`.

Dependencies:
- Includes `gxclio.h` for the command-list file abstraction and `strimpl.h` for stream internals.
- Pairs with `gxclmem.c` for implementation and `gxcllzw.c` for stream-state prototypes.

Research notes:
- Only `MEMFILE` and stream states are GC-compatible; the block and raw-buffer nodes are explicitly C-heap allocations managed by the memfile code.
- Reserve block chains are part of the public structure because low-memory write guarantees are fundamental to the clist memory backend.
