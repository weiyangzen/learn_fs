# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_kmem.c

Read completely: 653 lines.

Implements the kernel wired-memory allocator API layered over pool caches and UVM. Small allocations are rounded and served from size-class `pool_cache_t` arrays; larger allocations come from `kmem_va_arena`.

Core behavior:
- Size classes cover small caches up to 1024 bytes and selected larger caches up to a page, with alignment chosen around coherency units and page boundaries.
- `kmem_intr_alloc()`/`free()` are interrupt-capable allocation primitives.
- `kmem_alloc()`/`zalloc()`/`free()` assert non-interrupt context and integrate KMSAN marking.
- Large allocations use `uvm_km_kmem_alloc()`/`uvm_km_kmem_free()`.
- SDT probes expose allocation/free events per size class and for large allocations.
- Helpers provide `kmem_asprintf()`, string duplication/freeing, and stack-or-heap temporary buffers.

Debug and risks:
- DIAGNOSTIC hard kernels add a footer storing the requested size and panic on size-mismatched free.
- KASAN redzones adjust requested sizes and mark freed allocations.
- `LOCKDEBUG_MEM_CHECK` detects active locks inside memory being freed.
- Free callers must pass the original requested size.
