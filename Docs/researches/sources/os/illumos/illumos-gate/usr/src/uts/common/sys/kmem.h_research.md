# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kmem.h

## Purpose
Defines the kernel memory allocator client API, allocation flags, cache allocator API, and move-callback response types.

## Main Interfaces
- Allocation flags:
  - `KM_SLEEP`
  - `KM_NOSLEEP`
  - `KM_PANIC`
  - `KM_PUSHPAGE`
  - `KM_NORMALPRI`
  - `KM_NOSLEEP_LAZY`
  - `KM_VMFLAGS`
  - `KM_FLAGS`
- Basic allocator APIs:
  - `kmem_alloc()`
  - `kmem_zalloc()`
  - `kmem_free()`
  - `kmem_alloc_tryhard()`
  - `kmem_rezalloc()`
- Dump helpers:
  - `kmem_dump_init()`
  - `kmem_dump_begin()`
  - `kmem_dump_finish()`
- Cache flags:
  - `KMC_NOTOUCH`
  - `KMC_NODEBUG`
  - `KMC_NOMAGAZINE`
  - `KMC_NOHASH`
  - `KMC_QCACHE`
  - `KMC_KMEM_ALLOC`
  - `KMC_IDENTIFIER`
  - `KMC_PREFILL`
- `kmem_cache_t`: opaque cache type.
- `kmem_cbrc_t`: object move callback result enum.
- Cache APIs:
  - `kmem_cache_create()`
  - `kmem_cache_set_move()`
  - `kmem_cache_destroy()`
  - `kmem_cache_alloc()`
  - `kmem_cache_free()`
  - `kmem_cache_stat()`
  - `kmem_cache_reap_active()`
  - `kmem_cache_reap_soon()`
  - `kmem_cache_move_notify()`

## Dependencies And Relationships
Includes `sys/types.h` and `sys/vmem.h`. Kernel declarations are visible under `_KERNEL` or `_FAKE_KERNEL`.

## Research Notes
This is the stable allocator-facing header; implementation details are intentionally opaque. `POINTER_IS_VALID()` and `POINTER_INVALIDATE()` support clients implementing move callbacks by detecting kmem scribbles in freed memory.
