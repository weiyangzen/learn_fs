# sources/test-tools/fio/lib/memalign.c

Purpose: provides allocator-independent aligned allocation and matching free helpers.

Important APIs/functions: `__fio_memalign(size_t alignment, size_t size, malloc_fn fn)` and `__fio_memfree(void *ptr, size_t size, free_fn fn)`. An `align_footer` stored at `ret + size` records the offset from raw allocation to aligned pointer.

Control flow: allocation asserts power-of-two alignment, overallocates by alignment plus footer room, aligns the returned address, and records the raw-pointer offset. Free recomputes the footer location from the caller-provided size and frees `ptr - offset`.

State/persistence: no global state; metadata is persisted adjacent to the returned allocation and requires the same `size` at free time.

Dependencies/integration: includes `memalign.h` and `smalloc.h` but works with caller-supplied malloc/free functions. Useful for both libc and fio smalloc-style allocators.

Risks/test signals: passing a different size to free reads the wrong footer. Pointer arithmetic on `void *` relies on compiler extensions. Tests should cover alignments, zero/odd sizes, and mismatched allocator pairs under sanitizers.
