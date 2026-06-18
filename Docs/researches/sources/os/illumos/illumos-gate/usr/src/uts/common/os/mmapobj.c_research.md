# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mmapobj.c

## Purpose

Implements `mmapobj()`, the kernel object mapper used to map files either as flat private mappings or as interpreted executable objects. It understands ELF `ET_EXEC`, `ET_DYN`, `ET_REL`, and `ET_CORE` behavior; unsupported or small/non-ELF interpreted files fail with `ENOTSUP`. The file also implements a `lib_va` cache for ET_DYN objects so repeatedly mapped shared libraries can prefer stable virtual addresses when ASLR and padding do not disable the optimization.

## Main Entry Points

- `mmapobj()` dispatches flat vs interpreted mapping, validates padding and flags, handles `E2BIG` sizing for caller-provided `mmapobj_result_t` arrays.
- `mmapobj_unmap()` tears down partial or complete mappings, including ET_EXEC `/dev/null` reservation restoration and ET_DYN reservation-hole cleanup.
- `check_exec_addrs()` reserves fixed ET_EXEC address ranges or reuses prior `/dev/null` reservations.
- `mmapobj_map_interpret()` reads the initial header and routes ELF work through `doelfwork()`.
- `doelfwork()` validates ELF class/model/type, reads program headers with sleep/nosleep allocation policy, and calls `process_phdrs()`.
- `process_phdrs()` computes loadable spans, allocates/reserves start addresses, fills result descriptors, manages padding, updates the `lib_va` cache, and invokes `mmapobj_map_elf()`.
- `mmapobj_map_flat()`, `mmapobj_map_elf()`, and `mmapobj_map_ptload()` perform the actual vnode/address-space mapping and BSS zero-fill handling.

## Key Data and Algorithms

`struct lib_va` caches per-vnode identity, timestamps, preferred base VA, span, alignment, and up to `LIBVA_CACHED_SEGS` cached result descriptors. Cache lookup keys use fsid/nodeid plus ctime/mtime. Stale entries are removed immediately or marked `LV_DEL` until reference count reaches zero.

Address placement uses `map_addr()`, `as_gap()`, `valid_usr_range()`, `as_map()`, and per-model `lib_va_32_arena` / `lib_va_64_arena` vmem arenas. ASLR or requested padding disables the cache. 32-bit library VA reservation is limited by `lib_threshold`.

ELF segment processing recognizes `PT_LOAD` and `PT_SUNWBSS`, rejects overlapping mappings, handles non-power-of-two alignment by rounding, maps executable text with `MAP_TEXT`, maps data with `MAP_INITDATA`, and falls back to anonymous mapping plus `vn_rdwr()` when file offset and virtual address page offsets do not permit direct `VOP_MAP()`.

## Dependencies

This file sits directly on VM, VFS, ELF, process, and vnode interfaces: `as_*`, `segvn`, `segdev`, `VOP_MAP`, `VOP_GETATTR`, `vn_rdwr`, `valid_usr_range`, `map_addr`, process security flags, and filesystem `VFS_NOEXEC`.

## Correctness Notes

Important edge cases include noexec filesystems, ET_EXEC address collisions, partial failure cleanup after some segments are mapped, non-page-aligned ELF segments, BSS tail zeroing without permanent write permission, program-header allocation failure for very large tables, and avoiding reserved stack ranges. The cache uses mutexes and memory barriers so `lv_mps` is visible before `lv_num_segs` advertises valid cached descriptors.
