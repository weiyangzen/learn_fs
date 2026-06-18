# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_util.h

## Purpose
Declares shared NFSv4 ACL control-flag conversion helpers for xattr encoders.

## APIs, Types, And Control Flow
Exports `unsigned smb4acl_to_nfs4acl_flags(uint16_t smb4acl_flags)` and `uint16_t nfs4acl_to_smb4acl_flags(unsigned nfsacl41_flags)`. The functions convert between security descriptor DACL control bits and NFSv4.1 ACL flag bits.

## State, Dependencies, Integration
The header has no state. It relies on including contexts for integer typedefs and is used by XDR/NFS converters that need 4.1 control flag handling.

## Risks And Test Signals
The implementation is feature-gated by RPC XDR support, so declarations must only be linked from compatible build paths. Compile tests should cover `HAVE_RPC_XDR_H` on and off.
