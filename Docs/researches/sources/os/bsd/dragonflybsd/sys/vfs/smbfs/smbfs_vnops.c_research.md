# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_vnops.c

This file defines the SMBFS vnode operation vector and implements user-visible file operations on top of SMB protocol helpers.

Open validates type, handles directory open counts locally, validates cached mtimes, invalidates buffers on remote changes, opens remote files with read/write or read-only SMB access, stores cached credentials, and increments `n_opencount`. Close decrements open counts, closes directory search contexts, flushes buffers, closes remote FIDs, releases cached credentials, and invalidates attributes.

Attribute handling uses the short-lived cache from `smbfs_node.c`; cache misses call `smbfs_smb_lookup`. `setattr` supports file truncation through SMB writes, timestamp updates through the best available dialect-specific command, and rejects unsupported flags or read-only changes. Ownership and mode are mostly mount-option projections rather than remote SMB metadata.

Read, write, and readdir delegate to `smbfs_readvnode` and `smbfs_writevnode`. Create, remove, rename, mkdir, and rmdir use SMB wire helpers and update local vnode/name caches where possible. Hard links, symlinks, and mknod are unsupported.

Lookup performs path-component validation, read-only checks for mutating operations, access checks, remote lookup, and vnode allocation via `smbfs_nget`. It contains explicit logic for create/delete/rename lookup semantics and lock-parent behavior.

Other operations include a no-op fsync, logical bmap, synchronous-only strategy pass-through to `smbfs_doio`, unsupported ioctl, a `dosattr` extended attribute view, pathconf, vnode print, and advisory locking through local `lf_advlock` plus SMB byte-range locks.
