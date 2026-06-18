# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bp_map.c

## Purpose

`bp_map.c` maps `struct buf` data into kernel virtual address space for page I/O or physical I/O buffers, and provides copy helpers for buffers that may not already be kernel-addressable.

## Main Interfaces

Public APIs are `bp_init`, `bp_mapin_common`, `bp_mapin`, `bp_mapout`, `bp_copyout`, and `bp_copyin`.

Private helpers are `bp_vmem_alloc` and `bp_copy_common`.

## Behavior

`bp_init()` records required mapping alignment and HAT flags, and may create a dedicated `bp_map` vmem arena for cached aligned mappings.

`bp_mapin_common()` returns immediately for already remapped buffers, non-page/phys buffers, or physical I/O already in kernel address space. Otherwise it computes page offset, size, page count, and color alignment.

For single-page shadow/pageio buffers, it can use the kernel physical mapping fast path (`hat_kpm_mapin`). Otherwise it allocates aligned kernel virtual space, records `B_REMAPPED`, and maps each source page or PFN with `hat_devload()`.

`bp_mapout()` reverses the mapping, handling the KPM fast path separately. For ordinary mappings it flushes instruction memory on SPARC, unloads locked mappings, frees vmem space, and clears `B_REMAPPED`.

`bp_copy_common()` copies between driver memory and buffers. It uses direct `bcopy()` for ordinary KVA buffers, mapin/mapout when KPM is unavailable or forced off, and otherwise maps one page at a time with KPM for pageio, shadow, or user physical buffers.

## Notable Invariants

- A buffer cannot be both `B_PAGEIO` and `B_PHYS`.
- `B_REMAPPED` marks ownership of a temporary kernel mapping.
- Color alignment from `bp_color()` is preserved.
- Physical user VAs are translated through the process address space or `kas`.
- `bp_copy_common()` asserts requested copy range is within `b_bcount`.

## Dependencies

The file depends on `buf`, VM pages, KPM, HAT APIs, `vmem`, page coloring/alignment macros, address spaces, and platform instruction-cache flush support on SPARC.

## Research Notes

Important audit areas are PFN lookup failures for user VAs, page-list traversal with offsets, KPM mapout address correctness, and ensuring all `B_REMAPPED` paths are paired with `bp_mapout()`.
