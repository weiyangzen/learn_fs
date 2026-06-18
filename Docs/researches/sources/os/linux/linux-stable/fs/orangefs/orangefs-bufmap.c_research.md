# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-bufmap.c

## Scope

This file implements the shared-memory buffer map used for OrangeFS kernel/userspace data transfer and separate slot allocation for I/O and readdir.

## APIs Covered

- Slot map internals: install, kill, run down, get, put, wait for free.
- Bufmap lifecycle: `orangefs_bufmap_initialize()`, `orangefs_bufmap_finalize()`, `orangefs_bufmap_run_down()`.
- Slot APIs: `orangefs_bufmap_size_query()`, `orangefs_bufmap_get()`, `orangefs_bufmap_put()`, `orangefs_readdir_index_get()`, `orangefs_readdir_index_put()`.
- Copy APIs: `orangefs_bufmap_copy_from_iovec()`, `orangefs_bufmap_copy_to_iovec()`.

## Control Flow And Behavior

- Userspace supplies a page-aligned mapping descriptor; the kernel pins all pages with `pin_user_pages_fast(FOLL_WRITE)`.
- Pinned pages are grouped into folios, then split into descriptor records with per-descriptor folio arrays and offsets.
- Descriptor slots are tracked with bitmaps and wait queues; waiters can time out or be interrupted.
- Finalize marks slot maps as dying; run-down waits until all slots are returned, clears the global bufmap, unpins pages, and frees metadata.
- Data copies map folios locally, copy from/to iterators, and validate complete copies.
- A fast path handles the common case of a descriptor backed by exactly two 2 MiB folios for up to 4 MiB transfers.

## Risks And Invariants

- User descriptors must be page-aligned, internally size-consistent, and page-size divisible.
- All pinned pages must be unpinned on partial initialization failures and final teardown.
- Slot counter state uses negative values to represent uninstalled or dying maps.
- I/O and readdir use separate slot maps backed by different bitmaps.
