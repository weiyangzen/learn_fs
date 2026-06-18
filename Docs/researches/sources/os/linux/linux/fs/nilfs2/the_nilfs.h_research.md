# File Research: sources/os/linux/linux/fs/nilfs2/the_nilfs.h

Defines the shared NILFS2 in-memory supervisor object and mounted checkpoint root object.

Main contents:
- `struct the_nilfs`: per-block-device NILFS state shared across mount points.
- `struct nilfs_root`: per-mounted-checkpoint/snapshot state.
- State flags: initialized, discontinued, GC running, superblock dirty, purging.
- Mount option helpers.
- Segment geometry helpers.
- Superblock update helpers.
- Function prototypes implemented by `the_nilfs.c`.

Important state categories in `struct the_nilfs`:
- Back pointers: superblock, block device.
- Superblock buffers and parsed superblock state.
- Segment constructor cursor and write timestamps.
- Latest segment cursor protected by `ns_last_segment_lock`.
- Metadata files: DAT, CPFILE, SUFILE.
- Mounted checkpoint rb-tree and lock.
- Dirty file list and GC inode list.
- Mount options and reserved block ownership.
- Disk layout: block size, segment count, blocks per segment, inode size, CRC seed.
- Sysfs per-device kobject and subgroup pointer.

Inline behavior:
- `nilfs_sb_need_update()` checks time-based superblock update frequency.
- `nilfs_sb_will_flip()` determines superblock write target flip pattern from write count.
- Segment range/start/number helpers translate segment numbers and block numbers.
- `nilfs_flush_device()` issues a block-device flush once when barriers are enabled, with a write memory barrier before the flush.

Dependencies:
- Kernel buffer-head, rb-tree, fs, block-device, slab, and refcount APIs.
- Forward declarations for segment constructor and sysfs subgroup state.

Risk notes:
- The sysfs fields embedded here make `the_nilfs` lifecycle tightly coupled to `sysfs.c`.
- Several inline helpers assume valid initialized geometry; callers must not use them before `init_nilfs()` has completed.
