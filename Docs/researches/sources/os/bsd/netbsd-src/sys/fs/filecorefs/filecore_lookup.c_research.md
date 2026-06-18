# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_lookup.c

Read completely: 286 lines.

Implements FileCore pathname lookup. It follows a UFS-like lookup outline but is read-only: it checks directory execute permission, rejects delete/rename on read-only final components, consults the name cache, then linearly scans the fixed-size FileCore directory entries.

The scan can begin at `i_diroff` from a previous successful lookup and wrap once for a second pass. Names are compared with `filecore_fncmp()`, which handles FileCore’s name encoding and case behavior. `.` returns the directory vnode itself, and `..` resolves through `filecore_getparent()`.

For normal entries, the child inode number is synthesized from the parent directory’s FileCore address plus the directory entry index shifted into the high inode bits. Missing names are cached negatively and return `EROFS` for create/rename attempts or `ENOENT` otherwise.
