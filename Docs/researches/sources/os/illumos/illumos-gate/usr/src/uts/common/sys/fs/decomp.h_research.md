# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/decomp.h

This header defines a generic compressed-file header format and kernel decompression vnode wrapper state.

Compressed header:
- Magic values distinguish ZLIB and GZIP.
- Version is `CH_VERSION` 1.
- Algorithm id `CH_ALG_ZLIB` is 1.
- `struct comphdr` contains magic, version, algorithm, uncompressed file size, block size, and a variable-length block map.

Utility macro:
- `ZMAXBUF(n)` estimates the maximum compressed buffer size for zlib-style output.

Kernel decompression node:
- `struct dcnode` links a wrapper vnode to a backing vnode.
- Stores a buffer cache, lock, hash/LRU links, parsed compression header, header size, maximum zlib buffer size, and mapping count.
- Conversion macros map vnode to dcnode and dcnode to vnode.

Kernel API:
- `decompvp()` returns a decompression vnode wrapping a supplied vnode with credentials and caller context.

Dependencies and relationships:
- Provides decompression support as a vnode layer, not as a standalone filesystem.
- The block map in `comphdr` allows random access to compressed blocks.
