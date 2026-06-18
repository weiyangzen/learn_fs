# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_vnops.c

Implements NTFS vnode operations.

Key points:
- `ntfs_bmap()` is identity/no-op mapping for genfs.
- `ntfs_read()` bounds reads by `fnode` size and delegates to `ntfs_readattr()`.
- `ntfs_strategy()` handles buffer-cache reads through `ntfs_readattr()` and zero-fills partial EOF buffers; write strategy supports in-place writes but rejects file extension.
- `ntfs_write()` permits writes only within current file size and calls `ntfs_writeattr_plain()`.
- `ntfs_getattr()` synthesizes attributes from mount defaults, file-name timestamps, fnode size/allocation, and ntnode metadata.
- `ntfs_reclaim()` releases device vnode refs, destroys genfs state, frees `fnode` key/dir buffer, and releases/puts the ntnode.
- Access checks apply read-only mount restrictions for regular/dir/symlink writes and then use generic authorization with mount-wide uid/gid/mode.
- `ntfs_readdir()` emits synthetic `.` and `..`, then converts NTFS index entries to UTF-8 dirents and optional cookies.
- `ntfs_lookup()` handles namecache, `.`, `..`, parent lookup through `$FILE_NAME`, and normal directory search via `ntfs_ntlookupfile()`.
- `ntfs_fsync()` flushes vnode buffers, except `FSYNC_CACHE` returns `EOPNOTSUPP`.
- Pathconf reports NTFS limits.
- Vnode table wires creation/removal/link/rename/mkdir/rmdir/symlink/setattr/readlink to `genfs_eopnotsupp`.

Risk/notes:
- NTFS here is primarily read-oriented, but it has limited in-place write paths.
- Metadata-changing filesystem operations are intentionally unsupported.
