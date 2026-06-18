# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr.h

## Purpose
Shared configuration header for the `nfs4acl_xattr` VFS module and its encoding-specific converters.

## APIs, Types, And Control Flow
Defines `NFS4ACL_XDR_MAX_ACES` as 8192, `enum nfs4acl_encoding` with NDR, XDR, and NFS encodings, and `struct nfs4acl_config`. The config records NFS protocol version, encoding, xattr name, generic NFSv4 ACL parameters, default ACL style, whether NFS identities are numeric, and whether mode validation is enabled.

## State, Dependencies, Integration
The header declares configuration shape only. Runtime instances are attached to VFS handles by `vfs_nfs4acl_xattr.c` and consumed by `nfs4acl_xattr_ndr.c`, `nfs4acl_xattr_xdr.c`, and `nfs4acl_xattr_nfs.c`.

## Risks And Test Signals
The encoding enum drives persistent xattr interpretation, so mismatched config can make stored ACLs unreadable or incorrectly mapped. Test signals include initialization with each encoding, max ACE enforcement, version 4.0 versus 4.1 control flag behavior, numeric versus name ID modes, and custom xattr names.
