# File Research: sources/os/linux/linux/io_uring/memmap.c

Shared mapping-region implementation for io_uring rings, SQEs, provided buffer rings, parameter regions, and zero-copy receive regions.

Key flows:
- `io_pin_pages()` pins user pages for user-provided regions with overflow checks and long-term writable pins.
- `io_create_region()` validates `io_uring_region_desc`, accounts locked memory, either pins user pages or allocates kernel pages, and initializes a kernel pointer via direct page address or `vmap()`.
- `io_free_region()` unpins/releases pages, vunmaps if needed, unaccounts memory, and clears the descriptor.
- `io_mmap_get_region()` decodes mmap offsets for SQ/CQ ring, SQEs, pbuf rings, parameter region, and zcrx regions.
- MMU path validates non-user-provided regions, inserts pages with `vm_insert_pages()`, and supplies alias-safe `get_unmapped_area()`.
- NOMMU path maps direct kernel pointers, pins pages for VMA lifetime, and exposes direct mmap capabilities.

Important details:
- Region flags distinguish vmap, user-provided memory, and compound/single-ref allocation.
- `ctx->mmap_lock` protects mmap-visible region lookup and publication.
- User-provided regions cannot be mmaped back through the io_uring fd.
- SHM coloring support influences unmapped-area placement on aliasing architectures.
