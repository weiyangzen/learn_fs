# File Research: sources/virtualization/nbdkit/filters/xz/blkcache.h

This header declares the opaque `blkcache` type, cache statistics structure, and public cache operations used by the xz filter. `blkcache_stats` tracks hit and miss counters as `size_t`.

The API consists of `new_blkcache`, `free_blkcache`, `get_block`, `put_block`, and `blkcache_get_stats`, with nbdkit nonnull attributes on pointer parameters. `get_block` returns a borrowed cached data pointer and fills the containing block's start and size. `put_block` accepts ownership of a decompressed block buffer.

The closing include guard comment says `NBDKIT_XZFILE_H` even though the guard is `NBDKIT_BLKCACHE_H`; this is cosmetic but can confuse readers.
