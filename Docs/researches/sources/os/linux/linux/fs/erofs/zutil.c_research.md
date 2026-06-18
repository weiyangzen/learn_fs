# File Research: sources/os/linux/linux/fs/erofs/zutil.c

## Purpose
Provides shared compressed-EROFS utility infrastructure: global decompression buffers, reserved page allocation, pagepool release, and the global pcluster shrinker.

## Main Elements
- Global buffer pool: `struct z_erofs_gbuf`, `z_erofs_get_gbuf()`, and `z_erofs_put_gbuf()` provide per-CPU-indexed vmapped buffers protected by spinlocks and migration disabling.
- Buffer sizing: `z_erofs_gbuf_growsize()` grows all global buffers to a requested page count without shrinking existing buffers.
- Init/exit: `z_erofs_gbuf_init()` allocates buffer descriptors and an optional reserved-page pool; `z_erofs_gbuf_exit()` unmaps buffers, frees pages, and releases descriptors.
- Page allocation helpers: `__erofs_allocpage()` first uses a caller pagepool, then optional reserved pages, then `alloc_page()`; `erofs_release_pages()` returns pages to the reserved pool when possible or drops them.
- Shrinker registration: `erofs_shrinker_register()` and `erofs_shrinker_unregister()` add/remove mounted superblocks to a global list and drain managed pcluster slots during unmount.
- Shrinker callbacks: `erofs_shrink_count()` reports global reclaimable pcluster count, and `erofs_shrink_scan()` fairly iterates mounted EROFS superblocks, taking `umount_mutex` and calling `z_erofs_shrink_scan()`.
- Subsystem lifecycle: `erofs_init_shrinker()` allocates/registers the shrinker, and `erofs_exit_shrinker()` frees it.

## Dependencies And Integration
Used by compressed decompressor implementations and `zdata.c` for temporary buffers, emergency page allocation, pagepool handling, and reclaim of cached compressed pclusters across all mounted EROFS instances.

## Risk Notes
`z_erofs_get_gbuf()` relies on CPU migration being disabled so the selected buffer remains stable until `z_erofs_put_gbuf()`. Growing buffers must preserve old page arrays while safely swapping vmapped pointers under each buffer lock. The shrinker walks a global superblock list while coordinating with unmount through `umount_mutex`; failure to drain managed slots before unregistration would leave cached pclusters behind.
