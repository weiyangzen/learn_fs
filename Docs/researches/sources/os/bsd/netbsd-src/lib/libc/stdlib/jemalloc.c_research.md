# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/jemalloc.c

Read completely: 3870 lines.

In-tree NetBSD jemalloc implementation providing `malloc()`, `calloc()`, `realloc()`, `free()`, `posix_memalign()`, `malloc_usable_size()`, and fork hooks `_malloc_prefork()`, `_malloc_postfork()`, and `_malloc_postfork_child()`. It is a chunk/run/arena allocator designed for multiprocessor scalability, with per-CPU arenas, size classes, red-black trees for chunks/runs, and separate handling for small, large, and huge allocations.

Key structures: `chunk_node_t` tracks mapped chunk ranges; `arena_chunk_t` stores per-page run maps inside arena chunks; `arena_run_t` stores bitmaps for small allocations; `arena_bin_t` manages one size class; `arena_t` owns chunks, bins, a mutex, and an optional spare chunk. Small allocations use bin runs; large allocations use dedicated arena runs; huge allocations use whole chunks tracked in the global `huge` tree.

Memory comes from `mmap()` with `MAP_ALIGNED`, and on selected 32-bit architectures may also use `sbrk()`/`brk` to conserve address space. Freed chunks may be recorded in `old_chunks` for address reuse, and `MADV_FREE` is used when configured. Initialization reads CPU count, page size, `/etc/malloc.conf`, `MALLOC_OPTIONS` when safe, and compiled `_malloc_options`, then derives quantum, small-size, chunk-size, bin, and arena parameters.

Runtime options control abort-on-error, junk filling, memory advice, stats printing, ktrace `utrace`, SysV zero-size behavior, xmalloc aborts, and zero filling. Public APIs preserve expected malloc semantics: overflow is checked in `calloc()`, zero-size behavior depends on `opt_sysv`, `posix_memalign()` validates power-of-two alignment at least pointer-sized, and allocation failure sets `errno = ENOMEM` unless the xmalloc option aborts.

Risk areas are allocator-critical: lock ordering, red-black tree consistency, chunk/run map invariants, size-class rounding, overflow guards, and interactions with `mremap()`, `sbrk()`, `fork()`, and runtime initialization recursion.
