# File Research: sources/virtualization/nbdkit/filters/cow/blk.h

Purpose: internal API for COW overlay block operations.

Key details:
- Forward-declares `struct blk_overlay`.
- Declares global lifecycle `blk_load` and `blk_unload`.
- Declares per-overlay lifecycle `blk_create`, `blk_free`, and `blk_set_size`.
- Exposes `blk_status` for extent handling.
- Exposes block read/read-multiple, cache, write, and trim calls.
- Defines `enum cache_mode` for COW cache behavior: ignore, passthrough, read, or copy into overlay.

Integration notes:
- Used by `cow.c`; it hides temp-file sharding and bitmap details behind block-sized operations.
