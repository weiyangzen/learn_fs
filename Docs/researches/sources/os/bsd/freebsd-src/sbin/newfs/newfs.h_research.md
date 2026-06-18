# File Research: sources/os/bsd/freebsd-src/sbin/newfs/newfs.h

Shared declarations for the UFS `newfs` frontend and builder. It defines default fragment and block sizes, cylinder-group and inode-density defaults, and extern declarations for all option globals shared by `newfs.c` and `mkfs.c`.

Key contents:
- Defaults: `DFL_FRAGSIZE` 4096 and `DFL_BLKSIZE` 32768.
- `MAXBLKSPERCG`, `MAXBLKPG()`, and `NFPI` sizing policy constants.
- Externs for filesystem sizing, sector sizing, flags, tuning knobs, volume label, and `struct uufsd disk`.
- Documents the `part_ofs` workaround for file-backed partition offsets and libufs `bwrite()` limitations.
- Declares `void mkfs(struct partition *, char *)`.

Research notes:
- This header is the contract tying CLI option state to the UFS layout engine.
- The `part_ofs` comment is architecturally important because it explains a deliberate libufs bypass/hack.
