<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl_util.h -->
# sources/user-network-fs/samba/source3/modules/vfs_aixacl_util.h

## Purpose
This header declares the AIX classic ACL conversion helpers shared by AIX-specific VFS modules.

## Important APIs, Types, And Functions
It declares `aixacl_to_smbacl(struct acl *file_acl, TALLOC_CTX *mem_ctx)` and `aixacl_smb_to_aixacl(SMB_ACL_TYPE_T acltype, SMB_ACL_T theacl)`.

## Control Flow
The header has no runtime flow. It establishes the conversion API between platform ACL structures and Samba ACL structures.

## State And Persistence
No state is stored in the header. Implementations allocate converted ACLs and callers persist them through AIX ACL system calls.

## Dependencies And Integration Points
It depends on AIX `struct acl` and Samba ACL/talloc types being visible. It is included by `vfs_aixacl.c` and `vfs_aixacl2.c`.

## Risks
The header lacks include guards in the displayed source, so repeated inclusion depends on compiler tolerance and surrounding includes. It should only be used in AIX ACL builds where `struct acl` is defined.

## Test Signals
Compile/link tests in AIX builds confirm declaration compatibility. Behavioral testing belongs to `vfs_aixacl_util.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl_util.h -->
