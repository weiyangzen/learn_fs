# File Research: sources/os/linux/linux-stable/fs/gfs2/ops_fstype.c

Implements GFS2 filesystem type registration behavior: mount context parsing, superblock setup, lock protocol mounting, journal/statfs/quota/per-node initialization, remount/reconfigure, gfs2meta mounting, and superblock teardown.

Important behavior:
- `init_sbd()` allocates and initializes `struct gfs2_sbd`, waitqueues, locks, lists, counters, journal state, quota state, and default tune values.
- Superblock reading uses direct block-device I/O to avoid cached data, validates on-disk format/block sizes, derives pointer counts, hash sizing, directory reservation limits, and max metadata height.
- `init_names()` obtains lock protocol/table names from mount options or on-disk superblock.
- `gfs2_lm_mount()` selects `lock_nolock` or `lock_dlm`, parses hostdata, invokes the lock manager, and completes locking initialization.
- `init_locking()` acquires mount/live glocks and creates rename/freeze glocks.
- `init_sb()` locks and rereads the superblock, configures xattr handlers, block size, root dentry, and master dentry.
- `init_journal()` loads journal index entries, selects/locks this node’s journal, checks journal extents, initializes statfs inodes, and performs first-mounter or own-journal recovery.
- `init_per_node()` locates and locks the node-local quota-change file.
- `gfs2_fill_super()` ties all initialization together, creates workqueues/debug/sysfs entries, initializes inodes/rgrps/statfs/quota support, starts logd/quotad when writable, and makes the filesystem read-write when appropriate.
- Mount parameter parsing supports lock options, spectator/meta modes, ACLs, quota modes, data mode, discard, commit/statfs/quota intervals, barriers, rgrp LVBs, loccookie, and errors policy.
- `gfs2_reconfigure()` restricts immutable mount properties, handles ro/rw remounts, updates tune values, ACL/barrier flags, and emits online uevents.
- `gfs2meta` mounts attach to an existing GFS2 superblock and return the master directory.
- `gfs2_kill_sb()` flushes the log, drops root/master dentries, cooperatively evicts inodes, marks kill state, drains delete work, and kills the block superblock.

This file is the mount-state coordinator. Risk areas include unwind ordering, first-mount recovery boundaries, spectator read-only semantics, immutable remount validation, and teardown ordering while background work may still exist.
