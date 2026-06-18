# File Research: sources/local-fs/ocfs2-tools/libocfs2/memory.c

Provides libocfs2 memory allocation wrappers.

Generic allocation:
- `ocfs2_malloc(size, ptr)` allocates with `malloc()` and returns `OCFS2_ET_NO_MEMORY` on failure.
- `ocfs2_malloc0(size, ptr)` allocates and zeroes.
- `ocfs2_free(ptr)` frees `*ptr` and sets it to NULL.
- `ocfs2_realloc(size, ptr)` wraps `realloc()`.
- `ocfs2_realloc0(size, ptr, old_size)` reallocates and zeroes only the newly grown tail.

Block-aligned allocation:
- `ocfs2_malloc_blocks(channel, num_blocks, ptr)` allocates memory aligned to the IO channel block size using `posix_memalign()`.
- It checks multiplication overflow against `SIZE_MAX`.
- It probes with `malloc(bytes)` first because older glibc versions could abort inside `memalign()` on allocation failure.
- `ocfs2_malloc_block(channel, ptr)` allocates one block.

Role:
- Used throughout libocfs2 for disk block buffers that must satisfy direct/block IO alignment constraints.
- The API consistently accepts a pointer-to-pointer as `void *`, matching e2fsprogs-style allocation helpers.
