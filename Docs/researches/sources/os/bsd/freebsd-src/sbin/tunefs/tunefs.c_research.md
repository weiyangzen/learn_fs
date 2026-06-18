# File Research: sources/os/bsd/freebsd-src/sbin/tunefs/tunefs.c

## Purpose
Implements `tunefs`, which changes selected layout, policy, label, and feature flags on an existing UFS filesystem.

## Main Elements
- `main()` parses options for alternate superblocks, ACLs, max blocks per cylinder group, average file size, soft updates, soft updates journaling, GEOM journaling, metadata reserve, volume label, multilabel MAC, minfree, NFSv4 ACLs, optimization preference, print-only mode, average files per directory, journal size, and TRIM.
- Opens the target through `ufs_disk_fillout()` and refuses unsafe mutations when the filesystem is unclean unless only printing is requested.
- Updates `sblock` fields such as `fs_flags`, `fs_volname`, `fs_maxbpg`, `fs_avgfilesize`, `fs_metaspace`, `fs_minfree`, `fs_optim`, and `fs_avgfpdir`.
- Enforces mutual exclusion between POSIX.1e and NFSv4 ACLs, and between soft updates and GEOM journaling.
- `journal_alloc()` creates `.sujournal`: finds an inode, allocates direct/indirect blocks, initializes inode metadata, inserts it into the root directory, and updates cylinder groups.
- `journal_clear()` clears immutable/nounlink/nodump flags from an existing journal inode so it can be removed.
- Directory helpers locate and insert `.sujournal`, including extending root directory fragments into full blocks.
- `sbdirty()` marks the filesystem unclean and needing fsck after certain partial failures.
- `printfs()` reports current tunable state and optimization/minfree warnings.

## Dependencies And Integration
Uses `libufs`, UFS/FFS on-disk structures, cylinder group allocation helpers, directory entry formats, `chkdoreload()`, and mountpoint lookup.

## Risk Notes
This utility directly mutates filesystem metadata. The clean-filesystem gate, `sbdirty()` failure handling, and journal allocation paths are the central safety controls.
