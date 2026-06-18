# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_physmap.c

## Purpose
Builds compact physical segment lists from virtual address ranges, iovecs, or `vm_page` arrays, and provides helpers to temporarily map those physical segments into kernel virtual address space when needed.

## Main Entry Points
- `physmap_create_linear()` creates a physmap for a locked linear virtual range.
- `physmap_create_iov()` creates a physmap from a locked iovec array.
- `physmap_create_pagelist()` creates a physmap from an array of `vm_page` pointers.
- `physmap_destroy()` frees a physmap.
- `physmap_map_init()`, `physmap_map()`, and `physmap_map_fini()` iterate through temporary KVA mappings for physmap segments.
- `physmap_zero()` maps segments and zeroes a requested range.

## Control Flow And State
`physmap_alloc()` allocates a variable-sized `physmap_t` with room for the maximum possible segments. `physmap_fill()` walks virtual pages through `pmap_extract()`, coalescing physically contiguous pages into fewer segments while preserving offsets and lengths. Linear and iovec creation assume callers have already locked pages into memory.

Mapping uses a `physmap_cookie_t` cursor. `physmap_map_init()` skips to the segment containing the requested offset. Each `physmap_map()` releases the previous non-direct KVA mapping, advances to the next segment, tries MD direct mapping when available, and otherwise allocates VA-only kernel_map space, enters physical mappings with the requested protection, updates the pmap, and returns a KVA plus segment length. `physmap_map_fini()` removes the last temporary mapping and frees the cookie.

## Dependencies
Uses pmap extraction and kernel mappings, UVM page/KVA APIs, optional `mm_md_direct_mapped_phys()`, kmem, and physmap types from `<sys/physmap.h>`.

## Risks And Notes
Creation fails with `EFAULT` if any virtual page cannot be translated. Callers must supply locked/pinned backing pages for virtual ranges. `physmap_zero()` assumes each `physmap_map()` call yields a nonzero segment length until the requested length is exhausted. Temporary KVA mappings must be finalized to avoid leaking VA space.
