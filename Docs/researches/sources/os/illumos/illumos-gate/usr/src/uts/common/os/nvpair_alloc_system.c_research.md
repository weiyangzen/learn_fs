# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/nvpair_alloc_system.c

## Purpose

`nvpair_alloc_system.c` defines the default kernel memory allocators used by the nvpair/nvlist subsystem.

Read completely: 62 lines.

## Main Responsibilities

- Implements `nv_alloc_sys()` as a thin wrapper around `kmem_alloc()`.
- Implements `nv_free_sys()` as a thin wrapper around `kmem_free()`.
- Defines `system_ops`, an `nv_alloc_ops_t` table using those allocation functions.
- Exports `nv_alloc_sleep` and `nv_alloc_nosleep` defaults backed by `KM_SLEEP` and `KM_NOSLEEP`.

## Key Interfaces

`nv_alloc_sleep_def` stores `KM_SLEEP` in `nva_arg`; `nv_alloc_sys()` casts that argument back to the allocation flag passed to `kmem_alloc()`.

`nv_alloc_nosleep_def` does the same for `KM_NOSLEEP`.

The public pointers `nv_alloc_sleep` and `nv_alloc_nosleep` point at those defaults for kernel nvlist users.

## Notable Invariants

- The allocator operation table has no init, fini, or reset hooks.
- The free routine ignores `nva` and relies on the caller-provided size.
- Allocation behavior is entirely controlled by the `nva_arg` flag.

## Research Relevance

This file is small but important for fault-management and configuration paths that use nvlists in the kernel. In this group, `pcifm.c` uses nvlist-backed ereports; this allocator is the default backing mechanism for such structured kernel data.
