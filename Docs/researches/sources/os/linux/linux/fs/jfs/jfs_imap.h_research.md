# File Research: sources/os/linux/linux/fs/jfs/jfs_imap.h

## Role

Defines the inode allocation map on-disk structures, in-core control structures, geometry macros, and public imap API.

## Key Responsibilities

- Defines IAG geometry: 128 inode extents per IAG, 32 extents per summary word, 4 pages per inode extent, up to `MAXIAGS`, and up to 128 allocation groups.
- Provides inode-number conversion macros such as `INOTOIAG()`, `IAGTOLBLK()`, and `INOPBLK()`.
- Defines `struct iag`, including AG start, list links, summary maps, counts, padding, working/persistent allocation maps, and inode extent descriptors.
- Defines on-disk and in-core per-AG controls for free-inode/free-extent list heads and backed/free inode counts.
- Defines on-disk and in-core dinomap control pages, including free-IAG head, next IAG number, global counts, inode extent block geometry, and AG controls.
- Defines `struct inomap`, which wraps the in-core dinomap, inode-map inode pointer, free-list locks, per-AG locks, debug map pointer, and atomic global counts.
- Exposes shorthand macros for common in-core dinomap fields.
- Declares public imap operations for allocation, free, sync, persistent-map update, filesystem extension, mount/unmount, regular/special inode read/write, and special inode release.

## Important Interactions

- Includes `jfs_txnmgr.h` because persistent-map updates receive transaction blocks.
- Depends on geometry constants from `jfs_filsys.h` for inode counts, dinode size, and extent size.
- Used by `jfs_imap.c`, inode allocation code, transaction commit code, and mount/umount paths.

## Invariants and Risks

- `struct iag` and `struct dinomap_disk` are 4096-byte disk-format pages.
- `wmap` uses 1 bits for allocated working inodes; comments indicate 0 means free.
- Summary-map polarity is subtle: an `inosmap` bit is 0 when a backed extent has at least one free inode, and 1 when no allocatable backed free inode exists.
- In-core count fields mirror disk control-page fields but use native endianness and atomics for global counts.
