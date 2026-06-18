# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_node.c

## Purpose

Manages SMBFS vnode/private-node allocation, hash lookup, reclaim/inactive cleanup, and attribute caching.

## Main Entry Points

`smffs_hash()` computes an FNV-1 hash for names.

`smbfs_node_alloc()`:
- handles root/dotdot special cases.
- looks for existing vnodes with `vfs_hash_get()` using parent/name comparison.
- refreshes cached attributes on hits and kills stale vnodes whose file type no longer matches server attributes.
- allocates new vnode and `struct smbnode`, builds remote path, initializes vnode type/data, parent reference, inode number, and mount queue membership.
- inserts the vnode into the VFS hash and resolves races.

`smbfs_nget()` wraps node allocation using parent path and separator rules, then enters attributes if provided.

`smbfs_reclaim()` removes a vnode from the hash, frees name/path/node storage, clears vnode data, and releases referenced parent vnodes.

`smbfs_inactive()` closes open files or directory search contexts, invalidates buffers, sends SMB close for regular files, clears `NOPEN`, removes attr cache, and recycles nodes marked `NGONE`.

Attribute cache:
- `smbfs_attr_cacheenter()` updates cached size, mtime, DOS attrs, pager size, and attr timestamp.
- `smbfs_attr_cachelookup()` returns `ENOENT` for stale attrs older than two seconds, otherwise builds `struct vattr` from mount defaults, cached size/time, DOS flags, and share transmit size.

## Integration Points

Used by SMBFS lookup/readdir/create paths and by I/O code. It links VFS vnode identity to SMB remote paths and `netsmb` file attributes.

## Risks and Review Notes

Vnode identity is keyed by parent vnode plus name, while pseudo inode numbers are server-derived or hashed elsewhere. Rename/remove/server-side type changes require attr refresh and stale vnode teardown to avoid wrong vnode type reuse.
