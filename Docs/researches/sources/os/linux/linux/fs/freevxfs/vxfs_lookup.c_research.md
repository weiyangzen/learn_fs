# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_lookup.c

Read status: complete, 273 lines.

Purpose: implements FreeVxFS directory lookup and readdir.

Key flow:
- Defines directory inode ops with `.lookup = vxfs_lookup` and directory file ops with llseek/read/iterate/setlease.
- `vxfs_find_entry()` scans directory pages, skips each VxFS directory block header/hash overhead, advances by `d_reclen`, and matches name length and bytes.
- `vxfs_inode_by_name()` returns the inode number from a matching directory entry.
- `vxfs_lookup()` rejects names longer than `VXFS_NAMELEN`, resolves inode numbers, and returns `d_splice_alias()`.
- `vxfs_readdir()` emits `.` and `..`, scans directory records similarly to lookup, emits entries as `DT_UNKNOWN`, and updates `ctx->pos`.

Important dependencies: `vxfs_get_page`, `vxfs_put_page`, directory format helpers, `vxfs_iget`.

Risk notes:
- Directory parsing trusts on-disk `d_reclen`, `d_namelen`, and block overhead enough to drive iteration.
- Error from `vxfs_get_page()` in readdir is reported as `-ENOMEM` regardless of actual underlying error.
