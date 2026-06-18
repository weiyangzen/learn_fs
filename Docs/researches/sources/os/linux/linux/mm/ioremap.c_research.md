# File Research: sources/os/linux/linux/mm/ioremap.c

Generic implementation of ioremap/iounmap helpers.

`generic_ioremap_prot()`:
- Rejects calls before slab is available.
- Rejects zero-size and wraparound physical ranges.
- Page-aligns the physical address and size while preserving the original offset.
- Allocates a vmalloc area in `[IOREMAP_START, IOREMAP_END)` using `__get_vm_area_caller()`.
- Stores `phys_addr` in the `vm_struct`.
- Maps the range via `ioremap_page_range()`.
- Returns a tagged `__iomem` pointer with the original offset restored.

`ioremap_prot()` is exported when the architecture has not supplied its own macro/implementation.

`generic_iounmap()`:
- Masks to page boundary.
- Calls `vunmap()` only for addresses recognized by `is_ioremap_addr()`.

`iounmap()` is exported when not architecture-defined.

This file is a small generic fallback; architecture code may override the public names while still using these helpers.
