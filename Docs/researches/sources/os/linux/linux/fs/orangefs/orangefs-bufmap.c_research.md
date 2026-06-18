# File Research: sources/os/linux/linux/fs/orangefs/orangefs-bufmap.c

Implements OrangeFS shared buffer mapping and slot allocation between kernel and userspace daemon.

Key behavior:
- `slot_map` tracks available descriptor slots with a bitmap, count, and waitqueue for both read/write slots and readdir slots.
- `get()` waits for free slots with `slot_timeout_secs`; `put()` clears bitmap bits and wakes waiters.
- `orangefs_bufmap_initialize()` validates daemon-provided mapping alignment and sizing, allocates metadata, pins userspace pages, groups them into folios, slices folios into descriptors, installs slot maps, and publishes `__orangefs_bufmap`.
- `orangefs_bufmap_map()` pins pages with `pin_user_pages_fast(FOLL_WRITE)`, flushes dcache, groups pages into folios, records per-descriptor folio arrays/offsets, and detects the optimized two-2MiB-folio case.
- `orangefs_bufmap_finalize()` marks maps as killed; `orangefs_bufmap_run_down()` waits for active users to drain, unpins pages, frees metadata, and clears the global map.
- `orangefs_bufmap_get/put()` manage data I/O slots; `orangefs_readdir_index_get/put()` manage readdir indices.
- `orangefs_bufmap_copy_from_iovec()` and `orangefs_bufmap_copy_to_iovec()` copy between kernel iterators and daemon shared buffers using `kmap_local_folio()`, with a fast path for two 2MiB folios per 4MiB slot.

Important invariants:
- Descriptor size must be page-size aligned and total size must equal `size * count`.
- Active slots must drain before pinned user pages are unmapped during daemon shutdown.
