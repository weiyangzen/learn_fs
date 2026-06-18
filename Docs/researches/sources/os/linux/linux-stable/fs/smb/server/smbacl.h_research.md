# File Research: sources/os/linux/linux-stable/fs/smb/server/smbacl.h

## Summary
Declares ksmbd’s SMB ACL conversion API and supporting POSIX ACL state structures.

## Main Responsibilities
- Define security descriptor revision and control flag bits.
- Define `struct smb_fattr`, the intermediate owner/group/mode/access/POSIX-ACL container.
- Define POSIX ACL accumulation structures used while converting NT ACEs.
- Declare security descriptor parse/build, SID mapping, DACL inheritance, DACL permission checking, and security-info update functions.
- Provide idmapped-mount-aware POSIX ACL uid/gid translation helpers.

## Key Interfaces
`parse_sec_desc()`, `build_sec_desc()`, `smb_acl_sec_desc_scratch_len()`, `smb_inherit_dacl()`, `smb_check_perm_dacl()`, `set_info_sec()`, `id_to_sid()`, and `ksmbd_init_domain()` are the main exported contracts.

## Cross-File Interactions
Consumed by `smbacl.c`, `vfs.c`, SMB2 security query/set handlers, and xattr-backed NTACL storage.

## Risks
The structures here are shared conversion state. Changes to `smb_fattr` or ACL state layout affect both descriptor parsing and descriptor construction.
