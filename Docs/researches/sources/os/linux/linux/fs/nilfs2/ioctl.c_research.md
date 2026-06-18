# File Research: sources/os/linux/linux/fs/nilfs2/ioctl.c

This file implements NILFS2 ioctl handling for checkpoints, snapshots, segment usage, cleaner/GC operations, sync/checkpoint creation, resize, allocation-range control, FITRIM, file attributes, and filesystem labels.

User-buffer wrapper:
- `nilfs_ioctl_wrap_copy()` processes `struct nilfs_argv` arrays in page-sized chunks.
- It validates item size, count overflow, copies input when needed, calls a metadata callback, copies output when needed, and updates `v_nmembs` to the number processed.
- It prevents item sizes larger than a page and guards index/count overflow.

File attributes:
- `nilfs_fileattr_get()` exposes user-visible NILFS inode flags.
- `nilfs_fileattr_set()` rejects fsx attrs, masks allowed flags by inode mode, updates NILFS inode flags in a transaction, refreshes ctime, handles sync flag, and marks inode dirty.

Checkpoint/snapshot ioctls:
- `nilfs_ioctl_change_cpmode()` requires `CAP_SYS_ADMIN`, obtains write access, copies `nilfs_cpmode`, serializes with snapshot mount mutex, and calls `nilfs_cpfile_change_cpmode()` in a transaction.
- `nilfs_ioctl_delete_checkpoint()` deletes a single checkpoint in a transaction.
- `nilfs_ioctl_do_get_cpinfo()` and `nilfs_ioctl_get_cpstat()` expose cpfile information under `ns_segctor_sem`.

Segment/DAT info ioctls:
- SU info/stat callbacks query sufile under `ns_segctor_sem`.
- VINFO returns DAT virtual-block information.
- BDESCS maps DAT bmap offsets/levels to disk block numbers, returning zero for missing blocks.

Cleaner and GC:
- `nilfs_ioctl_move_inode_block()` stages a data or node block into GC inode caches and rejects conflicting buffers already on an association list.
- `nilfs_ioctl_move_blocks()` groups descriptors by inode/checkpoint, gets GC inodes, adds them to the GC inode list, stages all requested buffers, waits for reads, validates, marks them dirty, and cleans up on errors.
- `nilfs_ioctl_delete_checkpoints()` deletes checkpoint ranges for GC.
- `nilfs_ioctl_free_vblocknrs()` frees virtual block numbers through DAT.
- `nilfs_ioctl_mark_blocks_dirty()` verifies old block numbers still match live DAT bmap entries, then marks DAT or bmap node blocks dirty for copying.
- `nilfs_ioctl_prepare_clean_segments()` runs checkpoint deletion, virtual block freeing, and dirty marking in order, logging which phase failed.
- `nilfs_ioctl_clean_segments()` validates five argv vectors, imports user arrays, enforces per-segment bounds, serializes with `THE_NILFS_GC_RUNNING`, stages move blocks, calls `nilfs_clean_segments()`, removes all GC inodes, clears GC running state, and frees buffers.

Sync/resize/trim:
- `nilfs_ioctl_sync()` constructs a segment, flushes the device, and optionally returns the created checkpoint number.
- `nilfs_ioctl_resize()` requires admin and write access, then calls `nilfs_resize_fs()`.
- `nilfs_ioctl_trim_fs()` requires admin and discard support, clamps minimum length to discard granularity, and calls sufile trim under segment constructor semaphore.
- `nilfs_ioctl_set_alloc_range()` converts byte range to segment range and updates sufile allocation bounds.

Filesystem label:
- `nilfs_ioctl_get_fslabel()` reads the primary superblock label under `ns_sem`.
- `nilfs_ioctl_set_fslabel()` requires admin/write access, validates max label length, updates both superblocks when present, and commits the superblock.

Dispatch:
- `nilfs_ioctl()` dispatches FS version, checkpoint, SU, VINFO, BDESCS, clean segments, sync, resize, allocation range, FITRIM, and fslabel commands.
- `nilfs_compat_ioctl()` maps compat GETVERSION and passes compatible NILFS ioctls through with `compat_ptr()`.

Important security and correctness checks:
- Mutating administrative operations require `CAP_SYS_ADMIN` and often `mnt_want_write_file()`.
- User array sizes and counts are validated before allocation/copy.
- GC is serialized and explicitly cleans temporary GC inodes after each run.
- Segment-constructor semaphore protects metadata information queries against concurrent segment construction.
