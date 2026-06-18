# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_ndr.c

## Purpose
Converts between Samba `SMB4ACL_T` objects and Samba NDR-encoded `struct nfs4acl` blobs stored in extended attributes.

## APIs, Types, And Control Flow
Public functions are `nfs4acl_ndr_blob_to_smb4()` and `nfs4acl_smb4acl_to_ndr_blob()`. Blob-to-ACL pulls an NDR `nfs4acl`, creates an SMB4 ACL, maps versioned ACL flags to security descriptor control flags, then copies ACE type, flags, mask, numeric id, and special strings for owner/group/everyone into `SMB_ACE4PROP_T`. ACL-to-blob allocates a generated `struct nfs4acl`, copies SMB4 ACEs into it, maps control flags for versions above 4.0, emits special `e_who` strings or empty strings for numeric ids, optionally rejects ACLs with no special IDs under `nfs4acl_xattr:denymissingspecial`, and NDR-pushes the result.

## State, Dependencies, Integration
No durable state is held by the converter. It reads `struct nfs4acl_config` from the VFS handle and persists only the returned `DATA_BLOB` through its caller. Dependencies include generated NDR code, `nfs4_acls.h`, loadparm for `denymissingspecial`, and talloc.

## Risks And Test Signals
Unsupported special IDs are skipped without compacting the precomputed ACE count, which is worth regression coverage. Numeric identities carry an empty `e_who`, so readers depend on `e_id` and flags. Tests should cover NDR parse failures, all special identities, version 4.0 flag suppression, `denymissingspecial`, empty ACLs, malformed blobs, and round-trip stability.
