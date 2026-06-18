# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/fsck.h

Defines shared data structures, constants, state maps, and globals for `fsck_ext2fs`.

Important definitions:
- Limits for duplicate/bad blocks and buffer sizes.
- Inode state values: `USTATE`, `FSTATE`, `DSTATE`, `DFOUND`, `DCLEAR`, `FCLEAR`.
- `bufarea`, the checker’s small block buffer cache record.
- `inodesc`, the generic descriptor passed through block and directory scans.
- Duplicate block list and zero-link-count inode list structures.
- Directory inode cache structure `inoinfo`.
- Global ext2 superblock state, file descriptors, maps, counters, and flags.

Important macros:
- `dirty`, `initbarea`, and `sbdirty` for buffer/superblock dirty tracking.
- Block map operations `setbmap`, `testbmap`, `clrbmap`.
- Callback return flags `STOP`, `SKIP`, `KEEPON`, `ALTERED`, `FOUND`.

The header binds all ext2 fsck phases to shared mutable state: allocation maps, inode state, link counts, directory caches, duplicate block tracking, and superblock metadata.
