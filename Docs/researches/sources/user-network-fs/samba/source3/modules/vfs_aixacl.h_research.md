<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl.h -->
# sources/user-network-fs/samba/source3/modules/vfs_aixacl.h

## Purpose
This header declares the classic AIX ACL VFS helper functions implemented by `vfs_aixacl.c`. It allows related AIX ACL code to call or register the shared fd-based ACL operations.

## Important APIs, Types, And Functions
Declared functions are `aixacl_sys_acl_get_fd`, `aixacl_sys_acl_set_fd`, and `aixacl_sys_acl_delete_def_fd`. They use Samba `vfs_handle_struct`, `files_struct`, `SMB_ACL_TYPE_T`, `SMB_ACL_T`, and `TALLOC_CTX`.

## Control Flow
The header has no runtime control flow. It defines the signatures for get, set, and delete-default operations.

## State And Persistence
No state is defined here. Implementations persist ACL changes through AIX filesystem calls.

## Dependencies And Integration Points
It depends on Samba VFS and ACL types being visible to includers. It is part of the AIX-specific ACL integration boundary.

## Risks
The header intentionally exposes platform-specific functions; callers must compile only in builds with the corresponding AIX ACL support.

## Test Signals
Compile/link coverage in AIX builds validates the declarations. Runtime signals are supplied by `vfs_aixacl.c` tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl.h -->
