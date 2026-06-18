# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_io_compression_stats.h

## Scope

This header declares the I/O compression statistics entry points and constants shared by VFS code.

## APIs And Constants

- Declares `io_compression_stats_init(void)` and `io_compression_stats(buf_t bp)`.
- Defines default/min/max compression block sizes.
- Defines optional debug logging macro `io_compression_stats_dbg`.
- Defines `struct iocs_store_buffer`.
- Defines store-buffer sizing and notification thresholds.

## Dependencies And Role

Includes buffer and vnode headers. It is consumed by code that samples buffer writes and by vnode reclamation/stat dump logic.

## Risks And Invariants

- `IO_COMPRESSION_STATS_MAX_BLOCK_SIZE` permits very large per-CPU allocations.
- `IOCS_STORE_BUFFER_SIZE` depends on `struct iocs_store_buffer_entry`, which is defined outside this header.
- The header declares `io_compression_stats_init()`, while the implementation in this group does not define it.
