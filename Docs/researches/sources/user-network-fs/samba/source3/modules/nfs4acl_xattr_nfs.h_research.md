# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_nfs.h

## Purpose
Declares the NFS/kernel xattr encoding adapter for NFSv4 ACLs.

## APIs, Types, And Control Flow
Defines the persistent xattr name `NFS4ACL_NFS_XATTR_NAME` as `system.nfs4_acl`. Exports `nfs4acl_nfs_blob_to_smb4()` and `nfs4acl_smb4acl_to_nfs_blob()` for parsing and serializing ACL blobs. There is no inline control flow.

## State, Dependencies, Integration
The header is stateless and forward-declares `SMB4ACL_T`. It is included by the converter implementation and by `vfs_nfs4acl_xattr.c` when NFS encoding is configured.

## Risks And Test Signals
The xattr name is part of the storage contract. Tests should verify the VFS module selects this name by default for NFS encoding and rejects or reports unsupported conversion on platforms without RPC XDR support.
