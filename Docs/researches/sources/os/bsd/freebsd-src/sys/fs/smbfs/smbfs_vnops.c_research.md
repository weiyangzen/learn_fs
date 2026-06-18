# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_vnops.c

SMBFS vnode operation implementation for access checks, open/close, attributes, file I/O, namespace operations, directory reads, pathconf, strategy I/O, DOS extended attributes, byte-range locking, and lookup/namecache behavior.

Key responsibilities:
- Defines and registers `smbfs_vnodeops`, including access, open, close, getattr, setattr, read, write, create, remove, rename, mkdir, rmdir, readdir, strategy, lookup, pathconf, advisory locking, and DOS attribute extended-attribute reads.
- Synthesizes Unix access control from mount uid/gid plus configured file/dir mode and rejects writes to regular files, directories, and symlinks on read-only mounts.
- Opens regular files over SMB with `DENYNONE` sharing, preferring read-write handles on writable mounts and falling back to read-only opens when needed; directories are locally marked open.
- Invalidates buffers and attributes when cached modification times show server-side changes or local writes changed data.
- Implements `getattr()` through the SMBFS attribute cache, refreshing with `smbfs_smb_lookup()` on cache miss and preserving open-file local size.
- Implements `setattr()` for file truncation, DOS readonly/hidden/system/archive flag mapping, mode-to-readonly mapping, and timestamp updates through dialect/capability-specific SMB calls.
- Implements create, mkdir, remove, rmdir, and rename by issuing SMB create/delete/mkdir/rmdir/rename calls, then updating vnode/name caches and node `NGONE`/`NMODIFIED` flags.
- Leaves hard links, symlinks, and mknod unsupported with `EOPNOTSUPP`.
- Routes regular-file and directory reads through `smbfs_readvnode()` and writes through `smbfs_writevnode()`.
- Implements pathconf answers for max file size bits, name length, path length, truncation behavior, and hidden/system support based on SMB capabilities.
- Provides local-plus-remote advisory lock behavior: validates `flock` ranges, uses `lf_advlock()` locally, and mirrors set/unlock operations through `smbfs_smb_lock()`.
- Validates SMB path components, including backslash rejection and 8.3-era bad character/name length rules for old LANMAN dialects.
- Implements lookup with namecache integration, stale vnode type detection, dot/dotdot handling with mount busying, create/rename/delete last-component semantics, and `smbfs_nget()` vnode instantiation.
- Exposes the `dosattr` extended attribute as a six-character string representing readonly, hidden, system, volume, directory, and archive bits.

Dependencies:
- FreeBSD vnode operation, namecache, lockf, buffer, VM object, and directory lookup infrastructure.
- SMBFS node/mount state: `struct smbnode`, `struct smbmount`, `NOPEN`, `NMODIFIED`, `NGONE`, size/mtime/DOS attribute fields, parent references, and directory search sequence state.
- SMB wire helpers for open, close, lookup, create, delete, mkdir, rmdir, rename, set size, set attributes/times, read/write strategy I/O, and SMB byte-range locks.

Notable risks:
- Local Unix permissions are synthesized and do not necessarily match server ACL enforcement; the server remains authoritative.
- `setattr()` has several dialect-specific timestamp and attribute paths, including Win95 and non-NT-SMB behavior.
- `remove()` refuses open or multiply referenced regular vnodes, which avoids deleting active SMB nodes but differs from POSIX unlink semantics.
- Rename deletes the destination before renaming the source in the common path, so failure after deletion is not atomic.
- Lookup correctness depends on cache invalidation when server-side type changes are detected.
- Directory locking is not supported over SMB and returns `EOPNOTSUPP`.
