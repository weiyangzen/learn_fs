# File Research: sources/os/linux/linux-stable/fs/erofs/zutil.c

This file provides utility infrastructure for compressed EROFS: global decompression buffers, reserved page handling, pagepool release, and the global shrinker.

Major responsibilities:
- Defines per-CPU-ish global buffers (`struct z_erofs_gbuf`) used by decompressors.
- Exposes module parameters:
  - `global_buffers`
  - `reserved_pages`
- Initializes and exits the global buffer pool with `z_erofs_gbuf_init()` and `z_erofs_gbuf_exit()`.
- Allows global buffers to grow, never shrink, through `z_erofs_gbuf_growsize()`.
- Provides `z_erofs_get_gbuf()` / `z_erofs_put_gbuf()` with migration disabled and a per-buffer spinlock.
- Implements `__erofs_allocpage()` and `erofs_release_pages()` for decompression pagepool and reserved-page fallback.
- Maintains a global list of mounted EROFS superblocks participating in compressed-cache shrinking.
- Registers/unregisters each superblock with the shrinker list through `erofs_shrinker_register()` and `erofs_shrinker_unregister()`.
- Implements shrinker count/scan callbacks and global shrinker init/exit.

Important details:
- Buffer selection uses `raw_smp_processor_id() % z_erofs_gbuf_count`, guarded by `migrate_disable()` so the caller stays on the selected CPU while holding the buffer.
- Growing global buffers allocates any missing pages, vmaps a new buffer, swaps it under the buffer spinlock, and unmaps the old buffer afterward.
- Reserved pages are consumed before normal allocation when requested and are replenished before pages are released back to the allocator.
- Superblock shrinker unregister drains all managed pclusters before removing the superblock from the global list.
- Shrinker scans rotate processed superblocks to the list tail for fairness and use each superblock’s `umount_mutex` with trylock to avoid racing unmount.
- `erofs_global_shrink_cnt` is the global count hint used by the shrinker to decide whether work exists.
