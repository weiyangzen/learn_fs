# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsnode.h

## Purpose

`nfsnode.h` defines the per-vnode NFS client object, directory-cookie cache records, sillyrename state, cached directory entry format, vnode conversion macros, inline helpers, and vnode operation prototypes.

## Main Contents

- `struct sillyrename` stores delayed remove state for active unlinked files: credential, directory vnode, generated name length, and generated `.nfs...` name.
- `struct nfs_dirent` is the internal directory-entry format stored in NFS directory buffers.
- `struct nfsdmap` maps logical directory offsets to NFS cookies in groups of `NFSNUMCOOKIES`.
- `struct nfsnode` stores:
  - hash entry, current file size, cached revision, cached `vattr`, and attribute timestamp,
  - NFSv3 access cache fields,
  - last known mtime/ctime and lease expiry,
  - file handle pointer/inline file handle and size,
  - validated read/write credentials,
  - owning vnode, advisory lock state, saved write error,
  - unioned special-file time fields or directory cookie verifier/EOF/cookie list,
  - node flags and resize lock.
- Macros alias union fields for file vs directory use and convert `vnode`/`nfsnode`.
- Flags include flush-in-progress/wanted, local modified, write error, removed, special-file access/update/change, and remote modified.
- Inline helpers:
  - `nfs_rslock()`/`nfs_rsunlock()` serialize file-size changes.
  - `nfs_vpcred()` chooses stored write/read credentials or falls back to mount root credential.
- Prototypes expose write/inactive/reclaim/flush, sillyremove, nfsnode lookup, cookie lookup, and directory invalidation.

## Notable Details

- `NWANTED` is defined with the same bit value as `NACC` (`0x0100`), which is notable if both symbolic uses survive in code paths.
- File handles up to `NFS_SMALLFH` are stored inline; larger handles can be heap allocated, though `NFS_SMALLFH` defaults to 64.
- DragonFly does not pass ucreds directly to read/write vnode ops, so successful access/open stores credentials in the nfsnode for later I/O RPCs.

## Integration

Used by vnode operations in `nfs_vnops.c`, nfsnode allocation in `nfs_node.c`, buffer I/O in `nfs_bio.c`, and marshalling helpers that encode vnode file handles.
