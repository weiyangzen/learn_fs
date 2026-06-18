# File Research: sources/os/linux/linux/fs/nilfs2/the_nilfs.c

Implements lifecycle, mount-time initialization, superblock selection, recovery loading, space accounting, discard, and checkpoint-root management for `struct the_nilfs`.

Main responsibilities:
- Allocates and initializes `struct the_nilfs` with locks, lists, rb-tree root, default superblock update frequency, and dirty-block counters.
- Reads primary and secondary NILFS superblocks, validates magic/CRC/size, chooses the newest valid one, and handles fallback/swap.
- Stores disk layout from the superblock after validating revision, inode size, first inode, segment geometry, reserved segment percentage, and device-size bounds.
- Loads the latest super root and opens DAT, CPFILE, and SUFILE metadata files.
- Runs log scanning and recovery through `nilfs_search_super_root()` and `nilfs_salvage_orphan_logs()`.
- Creates the NILFS sysfs device group after metadata files are loaded and removes it on load/recovery failure.
- Provides segment discard coalescing over contiguous segment ranges.
- Counts free blocks from clean segment count and detects near-full state against reserved segments plus in-flight dirty data.
- Manages mounted checkpoint roots in an rb-tree, including sysfs snapshot group creation and deletion.

Key functions:
- `alloc_nilfs()` / `destroy_nilfs()`.
- `init_nilfs()` for superblock and disk layout initialization.
- `load_nilfs()` for super-root loading and recovery.
- `nilfs_set_last_segment()` for last written segment cursor and superblock dirty tracking.
- `nilfs_discard_segments()`, `nilfs_count_free_blocks()`, `nilfs_near_disk_full()`.
- `nilfs_lookup_root()`, `nilfs_find_or_create_root()`, `nilfs_put_root()`.

Concurrency and lifecycle:
- `ns_sem` protects shared superblock-derived mutable state.
- `ns_segctor_sem` protects log writer / segment-constructor state.
- `ns_last_segment_lock` protects latest partial segment cursor.
- `ns_cptree_lock` protects mounted checkpoint root rb-tree and refcount removal.
- `nilfs_find_or_create_root()` creates the rb-tree node before calling `nilfs_sysfs_create_snapshot_group()`; if sysfs creation fails, it frees the new node but does not erase it from the rb-tree in this file, which is a notable error-path concern.

Recovery behavior:
- If the filesystem is not clean, read-only mounts may temporarily enable write access for recovery unless `norecovery` or unsupported read-only compatible features prevent it.
- If primary super-root search fails with `-EINVAL`, it may roll back to the spare superblock when valid and consistent.
- After successful recovery, sets `NILFS_VALID_FS` and updates the superblock.

Dependencies:
- NILFS segment, allocation, checkpoint, segment-usage, DAT, and segment-buffer internals.
- Block device APIs for block size, read-only checks, flush/discard, and size.
- Sysfs device group functions from `sysfs.c`.

Risk notes:
- Error handling in `nilfs_find_or_create_root()` after sysfs snapshot creation failure appears incomplete because the inserted rb-node is not removed before freeing.
- Discard coalescing resets `nblocks` to zero after issuing a discard for a non-contiguous extent, then relies on later iterations to seed the next range; this matches the written control flow but should be reviewed carefully if modified.
