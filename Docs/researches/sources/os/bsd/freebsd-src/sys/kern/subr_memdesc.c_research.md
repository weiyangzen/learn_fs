# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_memdesc.c

## Purpose
Implements operations over generic memory descriptors (`struct memdesc`) that may describe virtual addresses, physical addresses, DMA segment lists, uios, mbufs, or VM page arrays. It provides data copy and external-mbuf construction helpers.

## Main Interfaces
- `memdesc_copyback()`: copy from a linear source buffer into descriptor-backed memory.
- `memdesc_copydata()`: copy descriptor-backed memory into a linear destination.
- `memdesc_alloc_ext_mbufs()`: create mbuf chains externally backed by memory described by the descriptor, optionally truncating final partial pages.

## Implementation Notes
Copy paths dispatch on `md_type`:
- `MEMDESC_VADDR`: direct `memcpy`.
- `MEMDESC_PADDR`: direct-map physical access via `PHYS_TO_DMAP`, requiring `PMAP_HAS_DMAP`.
- `MEMDESC_VLIST`: virtual DMA segments.
- `MEMDESC_PLIST`: physical DMA segments.
- `MEMDESC_MBUF`: `m_copyback()` / `m_copydata()`.
- `MEMDESC_VMPAGES`: `uiomove_fromphys()`.
- `MEMDESC_UIO`: intentionally rejected with panic; callers should use `uiomove`.

External mbuf allocation supports normal external buffers for virtual memory and `M_EXTPG` physical-page mbufs for physical addresses, physical segment lists, and VM pages. Helpers carefully handle page alignment, first-page offsets, full-page runs, last-page lengths, `MBUF_PEXT_MAX_PGS`, and optional truncation to avoid trailing partial pages.

## Dependencies
Uses VM page/pmap APIs, mbuf external page storage, bus DMA segments, uio, and `memdesc.h` callback types.

## Research Notes
This file is directly relevant to storage/network I/O boundaries: it provides a common way to treat physical pages, DMA lists, and mbufs uniformly while preserving zero-copy opportunities.
