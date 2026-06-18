# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfsnode.h

## Purpose
Defines the client-side `struct nfsnode`, the NFS equivalent of an inode attached to each active NFS vnode, plus related directory-cookie, access-cache, and sillyrename structures.

## Main Data
- `struct sillyrename` stores credentials, parent directory vnode, and temporary `.nfs...` name for deferred unlink of active files.
- `struct nfsdmap` stores logical directory offset to NFS cookie mappings in chunks of `NFSNUMCOOKIES`.
- `struct nfs_accesscache` caches NFS `ACCESS` result bits by UID and timestamp.
- `struct nfsnode` stores mutex-protected per-vnode state: file size, attribute cache, access cache, mtimes/change attributes, NFS file handle, vnode/parent pointers, lockf pointer, write error, special-file times or directory cookie verifier/EOF, sillyrename or directory cookie list, flags, direct I/O counters, NFSv4 node extension, and write credential.

## Flags
Important `n_flag` bits include directory cookie lock, fsync wait, modified/write-error state, create/truncate markers, size/cache invalidation markers, special-file access/update/change flags, delegation recall/modified flags, remove-in-progress/wait flags, node sleep lock flags, pNFS layout denial, write-open tracking, and “has been locked” tracking.

## Interfaces
Declares vnode/page/cache helpers implemented elsewhere: `ncl_getpages`, `ncl_putpages`, `ncl_write`, inactive/reclaim, `ncl_removeit`, `ncl_nget`, `ncl_getcookie`, directory invalidation, vnode lock upgrade/downgrade, and directory-cookie lock/unlock.

## Integration
Used directly by `nfs_clvnops.c` for nearly every vnode operation and by lower I/O and node-cache code.

## Risks
- Several unions reuse storage depending on vnode type, so callers must respect regular-file, directory, symlink, and special-file contexts.
- Many fields are protected by `n_mtx`; missed locking can corrupt cache stamps, flags, size, direct I/O counters, and sillyrename state.
