# sources/user-network-fs/samba/source3/modules/nfs4_acls.h

## Purpose
Public contract for Samba's NFSv4 ACL abstraction and NT ACL conversion helpers.

## APIs, Types, And Control Flow
The header defines `SMB_NFS4_ACEWHOID_T`, `SMB_ACE4PROP_T`, special identity constants, ACE type constants, NFSv4 flag and mask constants, opaque `SMB4ACL_T` and `SMB4ACE_T`, mode and duplicate policy enums, and `struct smbacl4_vfs_params`. It declares stat wrappers, ACL list construction and iteration helpers, control flag accessors, `nfs_ace_is_inherit`, NT ACL get/set conversion functions, and the native set callback type.

## State, Dependencies, Integration
No state is stored in the header. It requires Samba VFS, file, security descriptor, and talloc types from including contexts. It is the shared interface for native NFSv4 ACL modules and xattr-backed NFSv4 ACL encoders.

## Risks And Test Signals
The constants are semantic ABI: changing bit values breaks on-disk, wire, and conversion behavior. The opaque ACL list requires callers to use helper APIs rather than struct access. Compile tests should cover every module that includes it, and behavior tests should exercise each declared conversion entry point with both special and numeric identities.
