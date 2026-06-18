# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_xdr.c

## Purpose
Converts between `SMB4ACL_T` and a numeric NFSv4.1 XDR ACL representation stored in `security.nfs4acl_xdr`.

## APIs, Types, And Control Flow
Public functions are `nfs4acl_smb4acl_to_xdr_blob()` and `nfs4acl_xdr_blob_to_smb4()`. Serialization allocates a compact `nfsacl41i` with inline ACE array, maps control flags for versions above 4.0, converts special owner/group/everyone to `ACEI4_SPECIAL_WHO` numeric constants, copies uid/gid values for ordinary ACEs, computes fixed-size XDR blob length with max ACE and overflow checks, and encodes via `xdr_nfsacl41i`. Deserialization estimates ACE count from blob length, allocates an internal ACL, XDR-decodes, clears flags for version 4.0, maps special ids back to SMB4 special identities, copies uid/gid based on group flags, and appends ACEs to an SMB4 ACL.

## State, Dependencies, Integration
State is transient. Persistent data is the returned blob that callers put into xattrs. It depends on RPC XDR headers, `nfs41acl.h`, `nfs4acl_xattr_util`, and VFS handle configuration. Without RPC XDR headers, public functions return `NT_STATUS_NOT_SUPPORTED`.

## Risks And Test Signals
ACE count inference from blob size assumes the fixed internal layout and should be tested with truncated and padded blobs. Unsupported special IDs are skipped during conversion, and `smb_add_ace4()` return is not checked in deserialization. Tests should cover max ACE count, malformed XDR, version 4.0 flag clearing, special and numeric identities, group flag preservation, no-XDR builds, and round-trip byte stability for representative ACLs.
