# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_ndr.h

## Purpose
Declares NDR xattr conversion functions for NFSv4 ACL storage.

## APIs, Types, And Control Flow
Exports `nfs4acl_ndr_blob_to_smb4()` to parse a `DATA_BLOB` into an `SMB4ACL_T`, and `nfs4acl_smb4acl_to_ndr_blob()` to serialize an `SMB4ACL_T` into a blob. Both require a VFS handle for configuration and a talloc context for returned allocations.

## State, Dependencies, Integration
The header stores no state. It forward-declares `SMB4ACL_T` and relies on Samba VFS, NTSTATUS, talloc, and DATA_BLOB definitions supplied by including modules. It is consumed by `vfs_nfs4acl_xattr.c`.

## Risks And Test Signals
The declarations are the handoff between generic xattr VFS logic and NDR persistence. Compile and link tests should ensure the NDR converter is available whenever the NDR encoding is selectable.
