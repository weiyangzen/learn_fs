# File Research: sources/os/linux/linux-stable/fs/ntfs/malloc.h

## Summary
Provides small NTFS memory allocation wrappers for page-multiple allocations in filesystem contexts.

## Main Contents
- `__ntfs_malloc()` allocates one page via `kmalloc()` for sizes up to `PAGE_SIZE`, otherwise uses `__vmalloc()` when the requested page count is below total RAM pages.
- `ntfs_malloc_nofs()` applies `GFP_NOFS | __GFP_HIGHMEM`.
- `ntfs_malloc_nofs_nofail()` adds `__GFP_NOFAIL`.
- `ntfs_free()` releases memory with `kvfree()`.

## Important Behavior
Allocations are rounded conceptually to page multiples and are intended for NTFS code paths where filesystem reclaim recursion must be avoided. Small allocations deliberately allocate a full page through `kmalloc(PAGE_SIZE, ...)`.

## Risks
`__ntfs_malloc()` `BUG_ON`s zero-size requests. The nofail wrapper inherits the implementation comment saying it guarantees success, but the underlying helper can still return `NULL` for requests whose page count is at least total RAM pages.
