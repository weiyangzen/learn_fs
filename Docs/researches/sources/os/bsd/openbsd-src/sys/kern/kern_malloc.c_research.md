# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_malloc.c

## Purpose
Implements the kernel `malloc(9)` allocator over `kmem_map`, including bucketed small allocations, large page allocations, diagnostics, statistics, sysctl reporting, DDB printing, and overflow-safe `mallocarray()`.

## Main Responsibilities
- Computes bucket index with `BUCKETINDX()`.
- Allocates memory with `malloc()`.
- Frees memory with `free()`.
- Sizes kernel malloc arena with `kmeminit_nkmempages()`.
- Initializes `kmem_map`, buckets, usage metadata, stats names, and bucket strings in `kmeminit()`.
- Exports allocator state through `sysctl_malloc()`.
- Prints DDB malloc stats with `malloc_printit()`.
- Provides `mallocarray()` overflow checking.

## Allocation Behavior
Small allocations use power-of-two buckets. If a bucket freelist is empty, pages are allocated from `kmem_map`, split into bucket-sized elements, poisoned in diagnostic builds, and linked onto the freelist. Large allocations above `MAXALLOCSAVE` allocate rounded page ranges directly and record page count in `kmemusage`.

## Free Behavior
`free()` determines allocation size from `kmemusage`, validates bounds/alignment in diagnostic builds, detects likely double free by checking poison state and freelist membership, poisons freed objects, and returns small objects to bucket freelists or large objects to `kmem_map`.

## Key Data
- `kmem_map`, `kmembase`, `kmemlimit`, `kmemusage`.
- `bucket[MINBUCKET + 16]`.
- Optional `kmemstats[M_LAST]`.
- `malloc_mtx` protects bucket/stat state.
- `memname[]`, `memall`, and `buckstring` support diagnostics/sysctl.

## Arena Sizing
`kmeminit_nkmempages()` derives arena pages from physical memory, with caps based on `VM_KERNEL_SPACE_SIZE`, unless `nkmempages` is preconfigured.

## Dependencies
Uses UVM kernel maps, malloc type definitions, sysctl, mutexes, tracepoints, DDB, and optional KMEMSTATS/DIAGNOSTIC support.

## Research Notes
`mallocarray()` is a small but important safety wrapper: it panics or returns NULL on multiplication overflow depending on `M_CANFAIL`.
