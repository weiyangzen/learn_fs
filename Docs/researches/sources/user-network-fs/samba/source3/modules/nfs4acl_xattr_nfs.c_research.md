# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_nfs.c

## Purpose
Converts between `SMB4ACL_T` and kernel/NFS-style XDR ACL blobs stored under `system.nfs4_acl`. Unlike the internal XDR numeric format, this format stores NFSv4 who fields as UTF-8 strings such as `OWNER@`, numeric text, or user/group names.

## APIs, Types, And Control Flow
Public functions are `nfs4acl_smb4acl_to_nfs_blob()` and `nfs4acl_nfs_blob_to_smb4()`. The file supports NFSv4.0 and NFSv4.1 structures. Serialization maps SMB4 special IDs to NFS strings, maps uid/gid either to numeric strings when `nfs4_id_numeric` is set or to names via `getpwuid`/`getgrgid`, computes XDR blob sizes including aligned identifier lengths with overflow checks, and calls `xdr_nfsacl40` or `xdr_nfsacl41`. Deserialization XDR-decodes the configured version, maps special strings through a lookup table, maps group or user names/numbers with `nametogid`/`nametouid`, maps 4.1 flags to security descriptor control flags, and appends valid ACEs to a new SMB4 ACL.

## State, Dependencies, Integration
The converter has transient talloc/XDR state only. Persistent behavior is the encoded xattr blob returned to the caller. It depends on `<rpc/xdr.h>`, generated `nfs41acl.h`, passwd/group lookups, Samba id helpers, and `nfs4acl_xattr_util`. If RPC XDR headers are absent, both public functions return `NT_STATUS_NOT_SUPPORTED`.

## Risks And Test Signals
The biggest risk is silent ACE loss: unknown users, groups, unsupported special IDs, or unqualified nonnumeric names are skipped. Name service changes can make persisted name ACLs non-reproducible, so numeric mode should be tested separately. Additional tests should cover 4.0 versus 4.1 flags, overflow size guards, max ACE count, malformed XDR, special identities beyond owner/group/everyone, group flag preservation, and no-XDR build behavior.
