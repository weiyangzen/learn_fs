# File Research: sources/os/linux/linux-stable/fs/fuse/dax.c

## Purpose
Implements FUSE/virtiofs DAX support, mapping host page-cache memory into the guest address space and bypassing the guest page cache for eligible files.

## Key Structures
- `fuse_dax_mapping`: one DAX window range with inode, interval-tree node, busy/free list links, window offset, length, writability, and refcount.
- `fuse_inode_dax`: per-inode interval tree protected by an rwsem.
- `fuse_conn_dax`: per-connection DAX device, free/busy range lists, reclaim worker, waitqueue, and range counters.

## Key Interfaces
- Mapping setup/removal: `fuse_setup_one_mapping()`, `fuse_send_removemapping()`, `dmap_removemapping_list()`.
- Iomap integration: `fuse_iomap_begin()`, `fuse_iomap_end()`, `fuse_iomap_ops`.
- I/O paths: `fuse_dax_read_iter()`, `fuse_dax_write_iter()`, `fuse_dax_mmap()`, fault handlers.
- Reclaim: inline reclaim, worker reclaim, layout breaking, writeback/invalidation, and busy/free pool management.
- Lifecycle: `fuse_dax_conn_alloc()`, `fuse_dax_conn_free()`, `fuse_dax_inode_alloc()`, `fuse_dax_inode_cleanup()`, `fuse_dax_cancel_work()`.

## Design Notes
DAX ranges default to 2 MiB. Per-inode mappings are indexed by file-offset range and point into the connection DAX window. Read-only mappings can be upgraded to writable. Refcounts prevent reclaim while iomap/fault users hold a mapping. Reclaim takes `mapping->invalidate_lock`, breaks DAX layouts, invalidates page cache ranges, sends `FUSE_REMOVEMAPPING`, and returns mappings to the free pool.

## Dependencies
Uses DAX, iomap, interval trees, folios/page cache invalidation, FUSE setup/removemapping protocol messages, delayed work, and virtiofs-provided `dax_device`.

## Research Notes
File-extending writes deliberately fall back to FUSE direct I/O because DAX write and on-disk size extension are not atomic here. Fault-path allocation returns `-EAGAIN` rather than performing inline reclaim while invalidate locks are held.
