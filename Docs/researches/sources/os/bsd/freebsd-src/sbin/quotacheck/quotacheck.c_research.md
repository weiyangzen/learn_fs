# File Research: sources/os/bsd/freebsd-src/sbin/quotacheck/quotacheck.c

Main UFS quota checker and quota usage reconciler.

Key elements:
- `main` parses `-a`, `-c 32|64`, `-g`, `-u`, `-v`, and deprecated `-l`; preloads passwd/group ids into hash tables; dispatches either all-fstab checking via `checkfstab` or selected filesystem checking.
- `chkquota` optionally converts quota format, opens the raw filesystem, reads the UFS superblock through `sbget`, scans cylinder groups and allocated inodes, skips invalid negative-looking IDs, snapshot files, and quota files themselves, accumulates per-user/per-group inode and block usage, then updates quota files.
- `update` compares accumulated usage to existing `dqblk` records, writes changed usage with `quota_write_usage`, handles ids beyond current quota file max id, and truncates stale tail records when safe.
- `lookup`/`addid` maintain per-quota-type hash tables of `fileusage` records.
- `setinodebuf`, `getnextinode`, and `freeinodebuf` implement buffered sequential inode reads per cylinder group.
- `blkread` seeks and reads raw filesystem blocks using the filesystem device block size.
- `printchanges` reports verbose before/after usage fixes.

Dependencies:
- UFS/FFS headers, libufs, libutil quota APIs, fstab/passwd/group databases, shared `blockcheck`, and `checkfstab`.

Research notes:
- The scanner has separate UFS1/UFS2 inode field access through the `DIP` macro.
- Soft updates filesystems use cylinder group inode allocation maps to reduce scanning.
- Some early error returns after opening the device do not close `fi`; the process is short-lived, but it is still a cleanup asymmetry.
