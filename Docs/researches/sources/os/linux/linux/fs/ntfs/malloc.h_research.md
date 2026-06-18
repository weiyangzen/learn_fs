# File Research: sources/os/linux/linux/fs/ntfs/malloc.h

This header provides small NTFS-local memory allocation wrappers.

Functions:
- `__ntfs_malloc(size, gfp_mask)` allocates page-sized-or-larger memory:
  - For `size <= PAGE_SIZE`, it uses `kmalloc(PAGE_SIZE, gfp_mask & ~__GFP_HIGHMEM)`.
  - For larger sizes below total RAM pages, it uses `__vmalloc(size, gfp_mask)`.
  - Returns `NULL` when the request is too large or allocation fails.
- `ntfs_malloc_nofs(size)` calls `__ntfs_malloc()` with `GFP_NOFS | __GFP_HIGHMEM`.
- `ntfs_malloc_nofs_nofail(size)` adds `__GFP_NOFAIL`.
- `ntfs_free(addr)` releases memory with `kvfree()`, matching either kmalloc or vmalloc backing.

Important behavior:
- Allocations are page-rounded by implementation behavior and intentionally avoid filesystem recursion through `GFP_NOFS`.
- The small-allocation path always allocates one full page, not the exact requested byte count.
- `BUG_ON(!size)` catches zero-sized allocations on the small path.

Role in subsystem:
This is a convenience layer for NTFS metadata buffers that may be backed by either slab or vmalloc memory and can be freed uniformly with `kvfree()`.
