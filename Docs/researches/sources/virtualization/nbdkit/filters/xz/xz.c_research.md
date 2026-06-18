# File Research: sources/virtualization/nbdkit/filters/xz/xz.c

This file implements the public `xz` filter callbacks. The filter presents an xz-compressed backend as a read-only uncompressed export, with per-connection decompressed-block caching. Configuration supports `xz-max-block` to cap allowed uncompressed block size and `xz-max-depth` to set cache depth.

`.open` always opens the underlying plugin read-only, allocates a handle, and creates a block cache. `.prepare` opens and validates the xz metadata through `xzfile_open`, then rejects files whose largest uncompressed block exceeds `xz-max-block`. `.get_size` returns the uncompressed size from the parsed xz index. The filter denies writes and extents, advertises multi-connection consistency, and uses cache emulation.

`.pread` first checks the local block cache. On miss it decompresses the xz block containing the requested offset via `xzfile_read_block`, inserts it into the cache, copies the requested slice, and recurses if the client request crosses block boundaries.

Risks and invariants: request serialization is forced with `NBDKIT_THREAD_MODEL_SERIALIZE_REQUESTS`, protecting the unsynchronized cache and liblzma state. Large xz blocks allocate full uncompressed block buffers. Recursive reads depend on xz index block coverage and progress across block boundaries.
