# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/aligned_alloc.c

Read completely: 70 lines.

Implements C11 `aligned_alloc(alignment, size)` on top of `posix_memalign()`. It verifies that alignment is nonzero and a power of two, raises it until it is at least `sizeof(void *)`, calls `posix_memalign()`, and maps any error return into `errno`.

Unlike strict C11 wording, this wrapper does not enforce that `size` is a multiple of `alignment`; behavior follows the underlying allocator for the requested size.
