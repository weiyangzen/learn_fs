# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_subr.c

Purpose: Miscellaneous CHFS helpers for memory accounting, directory lookup/output, size/flag changes, and timestamp updates.

Key entry points:
- `chfs_mem_info`: estimates available/total memory pages from UVM counters.
- `chfs_dir_lookup`: linear lookup in a directory inode’s `dents` list.
- `chfs_filldir`: builds a NetBSD `struct dirent` for readdir.
- `chfs_chsize`: vnode size change/truncate helper.
- `chfs_chflags`: file flag authorization and update helper.
- `chfs_itimes`, `chfs_update`: in-memory timestamp update helpers.

Important behavior:
- `chfs_chsize` rejects directory truncate, handles RO mounts, zeroes truncated ranges, truncates the fragment tree, and updates UVM/vnode/inode size.
- `chfs_chflags` follows NetBSD authorization rules for user/system flags and snapshots.
- `chfs_itimes` tracks pending timestamp changes using CHFS inode flags and sets `IN_ACCESSED`/`IN_MODIFIED`.

Dependencies:
- Uses kauth/genfs helpers for permissions.
- Uses `chfs_truncate_fragtree` from `chfs_readinode.c`.
- Used heavily by VOP setattr/write/close paths.

Research notes:
- `chfs_update` only updates in-memory times; persistence is performed by later `chfs_write_flash_vnode` callers.
- Directory lookup excludes physical `.` and `..`, which are synthesized by readdir/lookup.
