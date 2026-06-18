# File Research: sources/os/linux/linux/io_uring/memmap.h

Header for io_uring mapped regions.

Key contents:
- Defines special mmap offsets for parameter and zcrx regions.
- Declares page pinning, mmap, get_unmapped_area, region creation, and region freeing helpers.
- Inline helpers expose region pointer, set-state, size, and `io_region_publish()`, which copies a prepared region into a mmap-visible slot under `ctx->mmap_lock`.
