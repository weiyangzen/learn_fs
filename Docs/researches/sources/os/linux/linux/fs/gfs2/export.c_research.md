# File Research: sources/os/linux/linux/fs/gfs2/export.c

Implements GFS2 export operations for NFS file handles, parent lookup, and reverse name lookup.

Key entry points:
- `gfs2_encode_fh()`
- `gfs2_fh_to_dentry()`
- `gfs2_fh_to_parent()`
- `gfs2_get_name()`
- `gfs2_get_parent()`
- `gfs2_export_ops`

Important control flow:
- File handles encode formal inode number and disk address; parent handles append the same pair for the parent.
- Supports small, large, and old handle sizes.
- `gfs2_get_dentry()` rejects zero formal inode numbers as stale and looks up inodes by inum.
- `gfs2_get_name()` scans the parent directory under shared glock with a filldir actor that matches child block address and copies the name.
- `gfs2_get_parent()` resolves `..` through `gfs2_lookupi()`.

Dependencies and integration:
- Uses exportfs, GFS2 directory reading, inode lookup by inum, glocks, and dentry alias helpers.

Risks and invariants:
- Insufficient file handle buffers return `FILEID_INVALID` after updating the required length.
- Missing reverse name during export lookup returns `-ENOENT`.
- File handles rely on both formal inode number and disk address to detect stale references.
