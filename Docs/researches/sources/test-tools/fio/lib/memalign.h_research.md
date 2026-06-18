# sources/test-tools/fio/lib/memalign.h

Purpose: declares generic aligned allocation helpers and callback types.

Important APIs/types: `malloc_fn`, `free_fn`, `__fio_memalign`, and `__fio_memfree`.

Control flow/state: callers provide allocation/free callbacks, requested alignment, and size. The implementation stores hidden footer metadata and therefore requires free to receive the original size.

Dependencies/integration: includes integer and bool headers. Used by code that needs alignment without depending on `posix_memalign`.

Risks/test signals: callback signatures must match the allocator family, and the requested alignment must be a power of two. Tests should verify returned pointer alignment and correct freeing.
