<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/nolibc.c -->
## sources/test-tools/liburing/src/nolibc.c

Purpose: implements minimal memory primitives for `CONFIG_NOLIBC` builds so liburing can operate without standard libc allocation helpers.

Important APIs/types/functions: `__uring_memset` fills bytes manually. `struct uring_heap` stores allocation length before the returned pointer. `__uring_malloc` uses `__sys_mmap` for anonymous private memory and returns the payload after the header. `__uring_free` derives the header and unmaps the stored length.

Control flow: allocation size is increased by the heap header, mapped with read/write permissions, checked with `IS_ERR`, and later unmapped as one region. Null free is ignored.

State and persistence behavior: allocation length is persisted in-band immediately before the returned pointer. No allocator freelist exists; every allocation is its own mmap region.

Dependencies and integration points: depends on `lib.h` declarations and syscall wrappers from `syscall.h`. Used only when `lib.h` remaps `malloc`, `free`, and `memset`.

Risks: one-mmap-per-allocation is simple but expensive. Integer overflow around `len + sizeof(*heap)` is not explicitly guarded. Callers must only pass pointers returned by this allocator to `__uring_free`.

Test signals: setup/probe paths using allocation should continue to work in nolibc builds. Memory leak or munmap errors would show under sanitizers or platform-specific nolibc tests.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/nolibc.c -->
