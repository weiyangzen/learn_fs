# File Research: sources/os/linux/linux-stable/fs/nfs/nfs3_fs.h

## Purpose
NFSv3-specific internal declarations.

## Contents
- ACL declarations under `CONFIG_NFS_V3_ACL`:
  - `nfs3_get_acl()`
  - `nfs3_set_acl()`
  - `nfs3_proc_setacls()`
  - `nfs3_listxattr()`
- Stub behavior when ACL support is disabled:
  - `nfs3_proc_setacls()` returns success.
  - `nfs3_listxattr` is `NULL`.
- Client/server declarations:
  - `nfs3_create_server()`
  - `nfs3_clone_server()`
- Extern declaration for `nfs_v3`.

## Research Notes
This header connects NFSv3 ACL support, v3 client creation, and v3 module registration.
