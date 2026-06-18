# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_lookup.c

This file implements FreeVxFS directory lookup and directory iteration.

Major responsibilities:
- Define directory inode operations with `.lookup = vxfs_lookup`.
- Define directory file operations with generic seek/read, `vxfs_readdir`, and generic lease handling.
- Scan VxFS directory blocks linearly to find a matching directory entry.
- Resolve a dentry name to an inode number and then to a VFS inode.
- Emit `.` and `..` plus directory entries through `dir_emit()`.

Important design points:
- The driver does not use the on-disk directory hash chains; it scans records page by page.
- Directory block headers are skipped at filesystem block boundaries using `VXFS_DIRBLKOV()`.
- Directory scanning uses `vxfs_get_page()` and releases mapped pages with `vxfs_put_page()`.
- `ctx->pos` uses low bits to distinguish synthetic dot entries from real on-disk aligned positions.
- Directory entry types are emitted as `DT_UNKNOWN`, except synthetic `..` is emitted as `DT_DIR`.

Key invariants:
- Lookup rejects names longer than `VXFS_NAMELEN`.
- `d_reclen == 0` advances to the next filesystem block.
- Empty entries with `d_ino == 0` are skipped.
- Name comparison requires exact length and byte match.
- Found inodes are returned through `d_splice_alias()`.

External interfaces:
- Provides `vxfs_dir_inode_ops` and `vxfs_dir_operations` for `vxfs_iget()`.
