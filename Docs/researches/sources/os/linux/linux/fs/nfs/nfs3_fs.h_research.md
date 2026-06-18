# File Research: sources/os/linux/linux/fs/nfs/nfs3_fs.h

## Purpose
Declares NFSv3-specific filesystem interfaces for ACL support, server creation/cloning, and the NFSv3 subversion object.

## Main Interfaces
- Under `CONFIG_NFS_V3_ACL`, declares ACL get/set, SETACL RPC helper, and xattr listing.
- Without ACL support, `nfs3_proc_setacls()` is a no-op and `nfs3_listxattr` is `NULL`.
- Declares `nfs3_create_server()`, `nfs3_clone_server()`, and external `nfs_v3`.

## Research Notes
This header is the NFSv3-specific bridge between `nfs3proc.c`, `nfs3acl.c`, `nfs3client.c`, and module registration.
