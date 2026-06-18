# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_xdr.h

## Purpose
Declares the numeric XDR xattr adapter for NFSv4 ACL storage.

## APIs, Types, And Control Flow
Defines `NFS4ACL_XDR_XATTR_NAME` as `security.nfs4acl_xdr`. Exports `nfs4acl_xdr_blob_to_smb4()` and `nfs4acl_smb4acl_to_xdr_blob()` for converting between xattr blobs and `SMB4ACL_T`.

## State, Dependencies, Integration
The header has no state and forward-declares no local data beyond the xattr name. It is included by `vfs_nfs4acl_xattr.c` and the XDR converter implementation.

## Risks And Test Signals
The xattr name and function signatures are persistent integration contracts. Tests should ensure configured XDR encoding uses this name and that unsupported-platform return paths are handled by the caller.
