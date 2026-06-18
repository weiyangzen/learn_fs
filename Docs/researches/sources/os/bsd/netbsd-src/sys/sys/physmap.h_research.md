# File Research: sources/os/bsd/netbsd-src/sys/sys/physmap.h

## Purpose
Declares physical memory segment maps and helpers for creating, mapping, destroying, and zeroing physical mappings from user/kernel address descriptions.

## Main API
- Types: `physmap_segment_t`, `struct physmap`.
- Creation: `physmap_create_iov`, `physmap_create_linear`, `physmap_create_pagelist`.
- Destruction: `physmap_destroy`.
- Mapping lifecycle: `physmap_map_init`, `physmap_map`, `physmap_map_fini`.
- Utility: `physmap_zero`.

## Dependencies
Kernel/kmem-user only; includes `sys/types.h`, `sys/uio.h`, and `uvm/uvm_extern.h`.

## Risks and Notes
`struct physmap` uses a zero-length segment array, so allocation must size the object for `pm_maxsegs`. Mapping calls involve VM protections and address-space references; lifetime ordering matters.
