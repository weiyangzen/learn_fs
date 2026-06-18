# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_malloc.c

## Purpose
Provides the legacy `malloc(9)` wrapper interface on top of `kmem_intr_alloc/free`, including allocation headers, page-aligned large allocation handling, sanitizer redzones, and realloc semantics.

## Main Interfaces
- `kern_malloc(reqsize, flags)`: allocates memory for obsolete malloc callers, maps `M_NOWAIT` to `KM_NOSLEEP`, applies KASAN redzone sizing, stores total allocation size in a header, optionally zeros memory, and returns the payload.
- `kern_free(addr)`: recovers the hidden header, marks KASAN/KMSAN state, and frees either the small allocation or the page-aligned large allocation base.
- `kern_realloc(curaddr, newsize, flags)`: implements malloc/free special cases, sleepability assertion, grow-only reallocation, copy, and old-block free.

## Internal State And Dependencies
- Defines built-in malloc types such as `M_DEVBUF`, `M_TEMP`, `M_UFSMNT`, and network/routing buckets.
- `struct malloc_header` records allocation size and, under KASAN, requested size.
- Depends on `kmem_intr_alloc/free`, KASAN, KMSAN, and legacy `malloc/free` macros with `ksp`.

## Control Flow Notes
- Large allocations reserve an extra page so the returned payload can be page-aligned with the header immediately before it.
- Small allocations place the header at the beginning of the allocated block.
- `kern_realloc` returns the original pointer when the existing allocation is large enough; it never shrinks in place.

## Risk Areas
- Correct free depends on the header immediately preceding the user pointer.
- Large-allocation size arithmetic includes overflow handling by forcing a later allocation failure.
- KASAN requested-size tracking is necessary because real allocation size can include redzones.

## Filesystem Relevance
Indirect. Provides legacy kernel memory allocation used by many subsystems, including filesystem and VFS code.
