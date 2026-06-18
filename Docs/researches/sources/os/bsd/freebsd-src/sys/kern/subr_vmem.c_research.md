# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_vmem.c

## Purpose

Implements FreeBSD's `vmem(9)` resource arena allocator. It manages arbitrary address/resource ranges with boundary tags, size-class free lists, busy-tag hashing, optional import/release callbacks, small allocation quantum caches, and kernel debugger/diagnostic inspection.

## Main responsibilities

- Represents arenas with `struct vmem`, protected by an arena mutex/condvar.
- Represents ranges with `struct vmem_btag` boundary tags, typed as span, static span, free, busy, or next-fit cursor.
- Allocates/free resources through:
  - `vmem_alloc()`
  - `vmem_xalloc()`
  - `vmem_free()`
  - `vmem_xfree()`
  - `vmem_add()`
- Supports constrained allocation by alignment, phase, non-crossing boundary, min/max address, and fit strategy.
- Supports `M_BESTFIT`, `M_FIRSTFIT`, and `M_NEXTFIT`.
- Supports resource growth/shrink via `vmem_set_import()` and release callbacks.
- Tracks allocated tags in a hash table and periodically resizes it.
- Provides DDB commands and diagnostic consistency checking.

## Key data structures

- `struct vmem`
  - `vm_seglist`: ordered segment/boundary-tag list.
  - `vm_freelist[VMEM_MAXORDER]`: size-class free lists.
  - `vm_hashlist`: hash table for busy allocations, initially `vm_hash0`.
  - `vm_freetags`: per-arena reserve of unused boundary tags.
  - `vm_cursor`: next-fit cursor.
  - import/release/reclaim hooks and arena accounting.
- `struct vmem_btag`
  - start, size, type.
  - list linkage reused for free-list or busy-hash membership.
- Kernel-only `struct qcache`
  - UMA zone cache for small fixed-size resource allocations.

## Important control flow

- `vmem_init()` initializes locks, lists, hash table, cursor, quantum settings, optional initial static span, and inserts the arena into the global arena list.
- `bt_fill()` ensures enough preallocated boundary tags exist before operations that may split/import ranges.
- `vmem_xalloc()` rounds size to arena quantum, validates constraints, scans size-class free lists, clips a matching free tag, and records it as busy.
- `vmem_xalloc_nextfit()` scans from `vm_cursor`, coalesces around the cursor, and advances the cursor after successful allocation.
- `vmem_import()` asks the backing importer for more range, over-allocating for alignment when needed, then inserts the imported span.
- `vmem_xfree()` finds the busy tag by start address, marks it free, coalesces adjacent free tags, and may release an entire imported span back to the backing provider.
- `vmem_periodic()` walks all arenas to resize busy-tag hash tables, optionally run diagnostics, and wake waiters.

## Kernel integration

- Boot-time arenas include `kernel_arena`, `buffer_arena`, and `transient_arena`, plus `memguard_arena` under `DEBUG_MEMGUARD`.
- Boundary tags are allocated from UMA zone `vmem_bt_zone`.
- On platforms without `UMA_USE_DMAP`, `vmem_bt_alloc()` uses kernel arena address space and backing memory carefully to avoid allocator recursion.
- Small allocations can use UMA zcaches through `qc_init()`, `qc_import()`, and `qc_release()`.

## Filesystem/storage relevance

`vmem` is a foundational kernel resource allocator used by VM, kernel address-space, buffer, and device subsystems. Filesystem paths depend on these arenas indirectly for buffers, KVA-backed I/O, and kernel memory/resource management. The file is not a filesystem implementation, but it is part of the allocation substrate VFS and storage code rely on.

## Edge cases and safeguards

- Allocation constraints are asserted heavily with `MPASS`.
- Waiting allocations panic if they still fail after wait/reclaim/import paths.
- `bt_save()`/`bt_restore()` hide reserved tags while dropping the arena lock.
- Resource zero is avoided in quantum caches because UMA uses `0` as allocation failure.
- `vmem_try_release()` only releases whole imported spans.
- Diagnostic `vmem_check_sanity()` detects corrupt, overlapping, or invalid tags.

## Research notes

This file is mainly allocator infrastructure. For future source-tree-aligned indexing, classify it under kernel memory/resource management with cross-links to VM, buffer cache, and kernel address-space allocation rather than VFS semantics directly.
