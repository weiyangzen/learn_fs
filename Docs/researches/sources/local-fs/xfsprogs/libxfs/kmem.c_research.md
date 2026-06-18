# File Research: sources/local-fs/xfsprogs/libxfs/kmem.c

Userspace implementation of simple kernel-like memory/cache allocation helpers.

Key responsibilities:
- Creates/destroys `kmem_cache` descriptors.
- Allocates and zero-allocates fixed-size cache objects.
- Implements `kvmalloc`, `krealloc`, and `kasprintf`.

Important behavior:
- Allocation failures print an error and exit the process.
- `LIBXFS_LEAK_CHECK` causes `kmem_cache_destroy` to report nonzero outstanding allocations.
- `krealloc(ptr, 0, ...)` explicitly frees and returns NULL to match Linux behavior.

Dependencies:
- Uses libc malloc/calloc/realloc/free/vasprintf and global `progname`.

Notable risks:
- Constructors stored in `kmem_cache` are not invoked in allocation paths.
- Allocation counters are incremented but freeing must occur through matching cache-free code elsewhere.
