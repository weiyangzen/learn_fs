# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_vnops.c

## Scope

Implements LFS vnode operations and wrappers around ULFS behavior, including file creation/removal, directory operations, fsync, reclaim, strategy reads, cleaner/control fcntls, pageout queue flushing, and extended-attribute stubs.

## APIs And Behavior

- Vnode operation tables install LFS-specific handlers for regular files, special devices, and FIFOs while reusing many ULFS/genfs operations.
- `lfs_makeinode()` creates and initializes a new inode, writes it before its directory entry, inserts the directory entry, and rolls back on failure.
- `lfs_fsync()` writes dirty pages through `VOP_PUTPAGES`, updates metadata unless data-only, optionally syncs the device cache, and handles lazy sync by queuing pageout work.
- `lfs_set_dirop()`, `lfs_unset_dirop()`, `lfs_mark_vnode()`, and `lfs_unmark_vnode()` reserve space, exclude writers, track active/completed directory operations, and maintain `VU_DIROP` references.
- `lfs_create()`, `lfs_mknod()`, `lfs_symlink()`, `lfs_mkdir()`, `lfs_remove()`, `lfs_rmdir()`, and `lfs_link()` wrap ULFS mutations with LFS dirop accounting, update ordering, orphan handling, and read-only checks.
- `lfs_getattr()` reports inode state without forcing time updates; `lfs_setattr()` checks LFS buffer pressure before delegating to ULFS.
- `lfs_close()`, `lfsspec_close()`, and `lfsfifo_close()` update times and release log-wrap control when the controlling LWP closes root/Ifile.
- `lfs_reclaim()` frees unlinked inodes, clears modification state, removes unexpected pageout state, deregisters LFS metadata, and returns inode/dinode extensions to pools.
- `lfs_strategy()` handles reads by mapping logical blocks, avoiding races with cleaner-written intervals, and then issuing strategy I/O to the device vnode.
- `lfs_flush_dirops()` writes only completed dirop vnodes into a segment; `lfs_flush_pchain()` writes vnodes queued by lazy/pageout flushing.
- `lfs_fcntl()` is the modern root/Ifile control surface for cleaner wait/map/mark calls, reclaim, Ifile file handles, rewind/invalidate/resize, wrap-stop/wrap-go/wrap-pass controls, file fragmentation stats, segment/file rewrite requests, cleaner info, segment-use arrays, and autocleaner parameters.
- `lfs_filestats()` computes direct-block discontinuity metrics; `lfs_gop_size()` chooses fragment/block-rounded write extents; extattr handlers support ULFS1 only when configured and otherwise return unsupported.

## State And Dependencies

The file depends on ULFS lookup/readwrite/directory helpers, LFS reservation and segment writer APIs, vnode cache, UVM page state, buffer cache, authorization, cleaner syscall helpers, and LFS control structures. It mutates inode link counts, dinode fields, `IN_*` state flags, `VU_DIROP`, orphan state, pageout/dirop queues, and log-wrap state.

## Risks And Invariants

Directory updates must be bracketed by reservation and dirop marking so checkpoints cannot persist inconsistent inode/directory ordering. VU_DIROP vnodes carry extra references until safely unmarked. `lfs_strategy()` assumes cleaner checkpoints are synchronous enough for interval checks to protect reads. `lfs_fcntl()` exposes many privileged maintenance operations, so bounds checks on inode/segment arrays and mount-shutdown checks are central.
