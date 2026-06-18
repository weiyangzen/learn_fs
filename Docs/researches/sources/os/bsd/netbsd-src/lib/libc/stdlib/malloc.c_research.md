# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/malloc.c

Implements NetBSD libc’s historical page/chunk allocator for `malloc()`, `calloc()`, `realloc()`, `free()`, and `posix_memalign()`. It tracks page ownership in a page directory, allocates large requests as whole-page runs, and serves small requests from per-size chunk pages with bitmaps.

Important behavior: initialization reads `/etc/malloc.conf`, `MALLOC_OPTIONS` when safe, and `_malloc_options` to enable abort-on-error, junk/zero fill, SysV `malloc(0)`, xmalloc, utrace, cache sizing, and `madvise` hints. It uses `sbrk`/`brk` for the heap and `mmap` for allocator metadata, preserves `errno` during initialization, and returns a special non-NULL `ZEROSIZEPTR` for zero-size allocations unless SysV mode is enabled.

Safety checks reject obviously invalid, modified, already-freed, or out-of-range pointers and can abort for privileged/sensitive processes. Threaded builds protect the public allocator path with a mutex and provide `_malloc_prefork()`, `_malloc_postfork()`, and `_malloc_postfork_child()` hooks.
