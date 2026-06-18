# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_subr.h

## Purpose
Shared internal SMBFS client declarations for find contexts, protocol helper entry points, VFS/node lifecycle helpers, cache helpers, XATTR helpers, ACL helpers, and SMBFS reader/writer lock wrappers.

## Main Definitions
- Debug/logging macros:
  - `SMBFSERR(...)`
  - `SMBVDEBUG(...)`
- Lock command constants:
  - `SMB_LOCK_EXCL`
  - `SMB_LOCK_SHARED`
  - `SMB_LOCK_RELEASE`
- Find context type enum:
  - `ft_LM1`
  - `ft_LM2`
  - `ft_SMB2`
  - `ft_XA`
- Find/read-directory flags:
  - `SMBFS_RDD_FINDFIRST`
  - `SMBFS_RDD_EOF`
  - `SMBFS_RDD_FINDSINGLE`
  - `SMBFS_RDD_NOCLOSE`
- `struct smbfs_fctx`
  - Carries find-first/find-next state, output attributes/name, SMB1/SMB2 request state, current response mdchain, resume keys, stream/XATTR scan state, and wildcard/filter data.
- `struct smb_fs_size_info`
  - Internal form of `FileFsFullSizeInformation`.

## Declared Functional Areas
- Common SMB operations:
  - Locks, get/set file attributes, statfs, open/create/rename/mkdir, findopen/findnext/findclose, security descriptor get/set.
- SMB1-specific operations:
  - Trans2 query, statfs, set EOF/disposition/attributes, rename variants, stream info, security descriptor operations.
- SMB2-specific operations:
  - Path/file attribute queries, statfs, set EOF/disposition/attributes, rename, directory enumeration, stream info, security descriptor operations.
- `smbfs_subr.c` helpers:
  - `smbfs_fullpath`
  - `smbfs_decode_dirent`
  - `smbfs_decode_file_all_info`
  - `smbfs_decode_fs_attr_info`
- VFS/module lifecycle:
  - `smbfs_vfsinit`, `smbfs_vfsfini`, `smbfs_subrinit`, `smbfs_subrfini`, `smbfs_clntinit`, `smbfs_clntfini`
- Mount/node/cache helpers:
  - zone list management, node table checks/destruction, flush paths, direct I/O, temporary name generation, AVL setup, node creation/lookup, cache validation/purge.
- Page and vnode helpers:
  - `smbfs_readvnode`, `smbfs_writevnode`, `smbfsgetattr`, `smbfs_invalidate_pages`.
- ACL helpers:
  - ID fetch/set, VSA get/set, raw SD ioctls.
- XATTR helpers:
  - fake xattr directory creation, xattr parent lookup, existence check, xattr attribute lookup, xattr find operations.
- Interruptible SMBFS rwlock wrappers:
  - `smbfs_rw_enter_sig`, `smbfs_rw_tryenter`, `smbfs_rw_exit`, `smbfs_rw_lock_held`, init/destroy.

## Important Interactions
- This header is the primary coupling point among SMBFS vnode ops, VFS ops, protocol-specific SMB1/SMB2 implementations, ACL handling, and XATTR/named-stream support.
- `smbfs_fctx` is shared by normal directory listings and XATTR stream listings.
