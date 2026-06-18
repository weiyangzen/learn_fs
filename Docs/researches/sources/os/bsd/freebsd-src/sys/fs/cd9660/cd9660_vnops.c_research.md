# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_vnops.c

Read completely: 870 lines.

Purpose: implements vnode operations for `cd9660` ISO9660 files, directories, symlinks, FIFOs, and buffer/page reads.

Key entry points:
- `cd9660_setattr()` rejects write-like metadata changes for read-only regular files/directories while allowing size no-ops for special nodes.
- `cd9660_access()` enforces read-only semantics for regular files, dirs, and symlinks, applies mount masks and uid/gid overrides, then calls `vaccess()`.
- `cd9660_open()` creates a vnode VM object sized from `iso_node`.
- `cd9660_getattr()` fills `vattr` from ISO/RRIP metadata and dynamically computes symlink size for zero-sized RRIP symlinks.
- `cd9660_ioctl()` supports `FIOGETLBA`.
- `cd9660_read()` maps file offsets to logical ISO blocks, uses clustered or sequential read-ahead, and moves data to userspace.
- `cd9660_readdir()` parses ISO directory records, validates record boundaries, supports RRIP names, ISO translation, Joliet names, associated-file pairing, and directory cookies.
- `cd9660_readlink()` extracts RRIP symbolic link target data from the directory record’s SUSP/RRIP fields.
- `cd9660_strategy()` maps logical vnode blocks to underlying device blocks via `iso_start`.
- `cd9660_getpages()` uses `vfs_bio_getpages()` by default, falling back to generic vnode pager via sysctl.

Important structures:
- `struct isoreaddir` maintains readdir state, saved/associated entries, cookies, offsets, and EOF handling.
- VOP vectors `cd9660_vnodeops` and `cd9660_fifoops` bind cd9660-specific and fifo-special behavior.

Behavior notes:
- Directory parsing defends against zero-length records, too-short records, and records crossing logical-block boundaries.
- POSIX pathconf reports 32-bit file size, link max 1, RRIP `NAME_MAX`, and RRIP symlink limits.
- `cd9660_vptofh()` serializes inode and start block into `struct ifid`.

Research notes:
- This file is the main bridge from on-disk ISO records to FreeBSD VFS semantics.
- RRIP materially changes name, symlink, mode, and inode interpretation.
