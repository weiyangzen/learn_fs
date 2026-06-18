# File Research: sources/os/linux/linux/io_uring/rsrc.h

Header for io_uring registered resources, mapped buffers, and fixed-buffer import helpers.

Key responsibilities:
- Defines resource node types for files and buffers.
- Defines `io_mapped_ubuf`, folio coalescing metadata, and kernel-buffer flags.
- Declares resource cache/table allocation, registration, update, unregister, clone, memory accounting, and import helpers.
- Provides inline resource lookup, put, reset, vector reset, and KASAN-specific vector-cache cleanup helpers.

Important invariants:
- `io_put_rsrc_node()` and `io_reset_rsrc_node()` assert `ctx->uring_lock`.
- `refs` in `io_rsrc_node` is a simple lock-protected count, distinct from `io_mapped_ubuf::refs`.
- `IO_IMU_DEST` and `IO_IMU_SOURCE` map directly to iterator direction bits.
