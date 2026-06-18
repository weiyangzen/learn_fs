# File Research: sources/os/bsd/dragonflybsd/sys/sys/_malloc.h

Read completely: 180 lines.

This kernel-structure header defines DragonFlyBSD kmalloc slab allocator metadata and malloc-type accounting structures.

Key contents:
- Slab constants such as `KMALLOC_SLAB_SIZE`, `KMALLOC_SLAB_MAGIC`, and `KMALLOC_MAXFREEMAGS`.
- `struct kmalloc_slab` with lock state, type pointer, object size/count, circular free-object indices, existential lock state, bitmap, and free object array.
- `struct kmalloc_mgt` for per-CPU and global slab lists.
- `struct kmalloc_use` for per-CPU usage statistics and local object storage.
- `struct malloc_type`, `malloc_type_t`, `MALLOC_DECLARE`, allocator flags, and `KMGlobalData`.

Important interactions:
- Intended only for `_KERNEL` or `_KERNEL_STRUCTURES`, especially consumers like `sys/user.h`.
- Uses spinlocks, exislocks, cache alignment, and SMP CPU sizing.

Security/reliability notes:
- This is allocator-internal ABI. Incorrect structure layout or flag interpretation can corrupt kernel memory accounting and slab free lists.
- Double-free checking is enabled by `KMALLOC_CHECK_DOUBLE_FREE`.
