# File Research: sources/os/linux/linux/fs/fuse/dax.c

## Purpose
This file implements FUSE/virtiofs DAX direct host memory access. It maps file offsets into a shared DAX window using daemon-mediated `FUSE_SETUPMAPPING` and `FUSE_REMOVEMAPPING` requests, integrates with iomap/DAX read-write and mmap fault paths, and reclaims limited DAX window ranges.

## Main Definitions
- `FUSE_DAX_SHIFT` is 21, giving `FUSE_DAX_SZ` 2 MiB mapping ranges.
- `struct fuse_dax_mapping` describes one DAX window range mapped to an inode/file-offset interval.
- `struct fuse_inode_dax` stores each inode’s interval tree and lock.
- `struct fuse_conn_dax` stores the DAX device, global free/busy range lists, reclaim work, waitqueue, and counters.
- Mapping setup/removal functions include `fuse_setup_one_mapping()`, `fuse_send_removemapping()`, `dmap_removemapping_list()`, and `dmap_removemapping_one()`.
- Iomap operations are `fuse_iomap_begin()` and `fuse_iomap_end()`.
- Public I/O hooks include `fuse_dax_read_iter()`, `fuse_dax_write_iter()`, `fuse_dax_mmap()`, `fuse_dax_inode_init()`, `fuse_dax_inode_cleanup()`, and `fuse_dax_cancel_work()`.

## Control Flow And Behavior
The DAX connection initialization queries the DAX device size with `dax_direct_access()`, divides it into 2 MiB ranges, allocates one `fuse_dax_mapping` per range, and places all ranges on the free list. Per-inode DAX allocation initializes an interval tree guarded by an rwsem.

On iomap begin, the code looks for an existing mapping for the requested file offset. If it exists and write access is needed for a read-only mapping, it upgrades the mapping by sending another setup request. If no mapping exists and the offset is within EOF, it allocates or reclaims a free range, sends `FUSE_SETUPMAPPING`, inserts the mapping in the inode interval tree, adds it to the busy list, and returns an `IOMAP_MAPPED` DAX iomap. Reads beyond EOF return an `IOMAP_HOLE`.

Writes that extend file size avoid DAX iomap writes and instead use FUSE direct I/O so file data and size update do not become non-atomic. Non-extending reads/writes use `dax_iomap_rw()`. mmap faults use `dax_iomap_fault()` under `mapping->invalidate_lock` and retry with waitqueue sleeping when no DAX range is available.

Reclaim can happen inline or from delayed work. It avoids ranges with refcount greater than one, breaks DAX layouts, writes back and invalidates page cache, removes the interval-tree entry, sends `FUSE_REMOVEMAPPING`, and returns the mapping to the free pool. Inode eviction reclaims all mappings without taking normal inode DAX locks because reclaim lock ordering would otherwise trip lock validation.

## Dependencies And Interfaces
The file depends on DAX, iomap, interval trees, FUSE request helpers, address-space invalidation, page-fault accounting, and virtiofs/FUSE DAX negotiation fields. It is built only under `CONFIG_FUSE_DAX`.

## Concurrency And Safety
There are three main synchronization layers: `fcd->lock` for global free/busy lists, per-inode `fi->dax->sem` for interval tree changes and lookup stability, and `mapping->invalidate_lock` for page-cache/fault exclusion during reclaim. Mapping refcounts prevent reclaim while iomap users hold active references.

## Research Notes
The DAX window is a scarce cache of file mappings, not a permanent block mapping. The code is careful around fault-path restrictions: it returns `-EAGAIN` instead of doing inline reclaim when holding locks that reclaim would need to drop.
