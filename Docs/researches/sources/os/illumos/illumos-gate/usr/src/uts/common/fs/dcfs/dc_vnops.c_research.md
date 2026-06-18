# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dcfs/dc_vnops.c

This file implements `dcfs`, a layered pseudo filesystem that presents UFS fiocompressed files as transparently decompressed read-only regular files. UFS detects compressed files and calls `decompvp()` to obtain a shadow dcfs vnode.

Major components:
- Module registration for filesystem type `dcfs`.
- A vnode operation table for open, close, read, getattr, setattr, access, fsync, inactive, fid, seek, frlock, realvp, getpage, putpage, map, addmap, and delmap.
- `dcnode` allocation, recycling, hash-table lookup by subordinate vnode, and small LRU retention for nodes with cached pages.
- Decompression block handling through zlib-compatible `z_uncompress()` and a per-block-size kmem cache.

Control flow:
- `decompvp()` checks whether a shadow vnode already exists, validates the compressed header, reads the full block map, allocates a `dcnode`, holds the subordinate vnode, initializes decompression buffer cache state, and inserts the node into `dctable`.
- `dc_read()` reads through `segmap`; actual decompression occurs in page-fault/page-cache paths.
- `dc_getpage()` rounds the requested range to compression-block boundaries and calls `dc_getblock()` per block.
- `dc_getblock()` first tries cached pages and falls back to `dc_getblock_miss()`.
- `dc_getblock_miss()` reads compressed bytes from the subordinate vnode, decompresses into destination pages, zero-fills EOF slack, and validates decompressed size.
- `dc_putpage()` only supports invalidation/free/dontneed style cleanup; dirty pages are treated as impossible and forced out with error handling.
- `dc_map()`, `dc_addmap()`, and `dc_delmap()` support read mappings and track mapped page count for mandatory-lock checks.

The filesystem is intentionally read-only at the dcfs layer. Write attempts in `dc_getpage()` panic, and `dc_putapage()` also panics if a dirty page path is reached.

Important dependencies include vnode/VFS APIs, VM page APIs, `segmap`, `pvn_*` helpers, zlib wrapper functions, compressed file header definitions in `sys/fs/decomp.h`, and subordinate filesystem VOPs.

Risk areas:
- Header validation and block-map sizing are critical because compressed metadata drives later reads.
- Dirty-page paths are asserted impossible; any future write-like behavior would need explicit design.
- `dctable_lock` protects both hash and LRU operations, so lock ordering with vnode locks matters in inactive/recycle paths.
