# sources/user-network-fs/samba/source3/modules/vfs_posixacl.h

## Purpose
`vfs_posixacl.h` declares the public hook functions implemented by `vfs_posixacl.c`. It allows other Samba source files or module registration code to reference the POSIX ACL operations without exposing helper internals.

## Important APIs, Types, And Functions
- Declares `posixacl_sys_acl_get_fd`.
- Declares `posixacl_sys_acl_set_fd`.
- Declares `posixacl_sys_acl_delete_def_fd`.
- Uses Samba VFS and ACL types including `vfs_handle_struct`, `files_struct`, `SMB_ACL_TYPE_T`, `SMB_ACL_T`, and `TALLOC_CTX`.

## Control Flow
The header has no runtime control flow. It provides prototypes guarded by `__VFS_POSIXACL_H__`.

## State And Persistence
No state is defined here. Persistence behavior belongs to the implementation and the filesystem ACL layer.

## Dependencies And Integration Points
The header assumes including translation units already have the relevant Samba type definitions available through `includes.h` or module includes. It is included by `vfs_posixacl.c`.

## Risks
- Prototype drift between this header and `vfs_posixacl.c` would cause build failures or ABI mismatches.
- Because only public functions are declared, helper reuse requires editing the implementation or adding new declarations deliberately.

## Test Signals
- Full Samba/module build should validate prototypes.
- Any caller including the header should compile without duplicate or missing symbol warnings.
