# File Research: sources/os/linux/linux/fs/gfs2/dir.h

Declares GFS2 directory APIs, directory-add state, hash helpers, and dirent initialization helpers.

Key exports:
- `struct gfs2_diradd` holds allocation/search state for adding entries.
- `gfs2_dir_search()`, `gfs2_dir_check()`, `gfs2_dir_add()`, `gfs2_dir_del()`, `gfs2_dir_read()`, `gfs2_dir_mvino()`
- `gfs2_dir_exhash_dealloc()`
- `gfs2_diradd_alloc_required()`
- `gfs2_dir_get_new_buffer()`
- `gfs2_dir_hash_inval()`
- `gfs2_qdot`, `gfs2_qdotdot`

Inline helpers:
- `gfs2_disk_hash()` computes the on-disk CRC32 directory hash.
- `gfs2_str2qstr()` builds a hashed qstr from a string.
- `gfs2_qstr2dirent()` initializes an on-disk dirent skeleton from a qstr and record length.

Integration:
- Used by inode, dentry, export, bmap, and directory implementation paths.
