# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_malloc.c

Read completely: 1622 lines.

## Purpose
Implements FreeBSD's general-purpose kernel `malloc(9)` allocator on top of UMA, including fixed-size small allocation zones, page-backed large allocations, contiguous allocations, malloc type registration, per-CPU accounting, debugging hooks, and sysctl/DDB reporting.

## Main Elements
- Defines common malloc types `M_CACHE`, `M_DEVBUF`, and `M_TEMP`.
- Maintains `kmemzones[]` bucket zones from 16 bytes through 65536 bytes, with `kmemsize[]` mapping request sizes to zone indexes.
- `malloc()`, `malloc_domainset()`, `malloc_exec()`, `malloc_aligned()`, `mallocarray()`, and domain-aware variants allocate memory with type accounting.
- `free()`, `zfree()`, `realloc()`, `reallocf()`, `malloc_size()`, and `malloc_usable_size()` implement the normal allocator API.
- `contigmalloc()` and `contigmalloc_domainset()` allocate physically contiguous kernel memory through `kmem_alloc_contig*()`.
- Large and contiguous allocations are tagged through synthetic slab-cookie values so `free()` can distinguish UMA, large kmem, and contiguous allocations.
- `malloc_type_allocated()`, `malloc_type_freed()`, `malloc_init()`, and `malloc_uninit()` maintain per-type, per-CPU allocation statistics and leak warnings on type destruction.
- `kmeminit()` sizes the kernel memory arena from tunables, physical memory, KASAN/KMSAN shadow overhead, and architecture limits.
- `mallocinit()` initializes the UMA zones and size lookup table at `SI_SUB_KMEM`.
- Sysctls expose kmem sizing, malloc zone sizes/counts, malloc statistics, debug failure injection, and optional multi-zone debug separation.
- DDB support can show malloc type usage sorted by memory use.

## Dependencies And Integration
Uses UMA, kmem, vm domain sets, VM page accounting, KASAN/KMSAN, MemGuard, RedZone, DTrace malloc probes, DDB, sysctl, and the kernel `MALLOC_DEFINE` type framework. It underpins nearly every kernel subsystem in this group, including mbufs, modules, OSD, PMC, physio, and mutex pool allocation.

## Risk Notes
Allocator correctness depends on exact flag/context rules: `M_WAITOK` cannot be used from interrupt or sleep-prohibited contexts, sleep/spin critical sections are rejected under debug builds, and `M_EXEC` is forced down the large-allocation path. Slab-cookie tagging is central to safe `free()` and `malloc_usable_size()` behavior. `realloc()` intentionally does not fully rebalance per-type statistics for reused/copy paths, as noted in the source.
