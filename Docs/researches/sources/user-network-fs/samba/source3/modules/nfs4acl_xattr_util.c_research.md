# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_util.c

## Purpose
Small utility implementation for translating NFSv4 ACL flag bits and Samba security descriptor control flags.

## APIs, Types, And Control Flow
When `HAVE_RPC_XDR_H` is defined, exports `smb4acl_to_nfs4acl_flags(uint16_t)` and `nfs4acl_to_smb4acl_flags(unsigned)`. The first maps `SEC_DESC_DACL_AUTO_INHERITED`, `SEC_DESC_DACL_PROTECTED`, and `SEC_DESC_DACL_DEFAULTED` to `ACL4_AUTO_INHERIT`, `ACL4_PROTECTED`, and `ACL4_DEFAULTED`. The second maps those bits back and always starts the Samba control flags with `SEC_DESC_SELF_RELATIVE`.

## State, Dependencies, Integration
There is no state or persistence. Dependencies are Samba security descriptor constants and `nfs41acl.h` constants behind RPC XDR availability. The helpers are used by NFS and XDR xattr converters to avoid duplicating flag mapping.

## Risks And Test Signals
If compiled without RPC XDR support the header still declares functions, but this C file does not define them; consumers must also be guarded by the same build feature. Tests should compile both feature paths and validate exact bit mapping, including preservation of unrelated bits by omission.
