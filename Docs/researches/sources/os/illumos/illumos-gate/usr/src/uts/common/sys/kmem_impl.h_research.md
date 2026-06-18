# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kmem_impl.h

## Purpose
Defines private implementation structures and constants for the illumos slab/magazine kernel memory allocator.

## Main Interfaces
- Debug flags:
  - `KMF_AUDIT`
  - `KMF_DEADBEEF`
  - `KMF_REDZONE`
  - `KMF_CONTENTS`
  - `KMF_STICKY`
  - `KMF_NOMAGAZINE`
  - `KMF_FIREWALL`
  - `KMF_LITE`
  - `KMF_HASH`
  - `KMF_RANDOMIZE`
  - `KMF_DUMPDIVERT`
  - `KMF_DUMPUNSAFE`
  - `KMF_PREFILL`
- Debug patterns:
  - `KMEM_FREE_PATTERN`
  - `KMEM_UNINITIALIZED_PATTERN`
  - `KMEM_REDZONE_PATTERN`
  - `KMEM_REDZONE_BYTE`
- Size encoding helpers:
  - `KMEM_SIZE_ENCODE()`
  - `KMEM_SIZE_DECODE()`
  - `KMEM_SIZE_VALID()`
- Core structures:
  - `kmem_bufctl_t`
  - `kmem_bufctl_audit_t`
  - `kmem_buftag_t`
  - `kmem_buftag_lite_t`
  - `kmem_slab_t`
  - `kmem_magazine_t`
  - `kmem_magtype_t`
  - `kmem_cpu_cache_t`
  - `kmem_maglist_t`
  - `kmem_defrag_t`
  - `kmem_dump_t`
  - `struct kmem_cache`
  - `kmem_log_header_t`
  - `kmem_move_t`
- Addressing/layout helpers:
  - `KMEM_BUFTAG()`
  - `KMEM_BUFCTL()`
  - `KMEM_BUF()`
  - `KMEM_SLAB()`
  - `KMEM_CPU_CACHE()`
  - `KMEM_HASH()`
  - `KMEM_IS_MOVABLE()`

## Dependencies And Relationships
Includes allocator, vmem, thread/lock, kstat, CPU, page, AVL, and list headers. This header is consumed by allocator implementation and diagnostic code, not ordinary drivers.

## Research Notes
The file documents allocator lock order: cache lock, CPU cache locks by CPU ID, then depot lock. Per-CPU magazine caches are padded to `KMEM_CPU_CACHE_SIZE` for alignment/cache behavior. Defragmentation state tracks move callbacks, pending moves, dead slab lists, and client misuse checks.
