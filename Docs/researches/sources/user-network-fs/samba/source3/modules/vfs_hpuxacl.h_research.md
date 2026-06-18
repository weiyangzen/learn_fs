# sources/user-network-fs/samba/source3/modules/vfs_hpuxacl.h

Purpose: declares the public HP-UX ACL helper functions implemented by `vfs_hpuxacl.c` for use as Samba VFS POSIX ACL callbacks.

Important APIs/types/functions: prototypes cover `hpuxacl_sys_acl_get_file()`, `hpuxacl_sys_acl_get_fd()`, `hpuxacl_sys_acl_set_file()`, `hpuxacl_sys_acl_set_fd()`, and `hpuxacl_sys_acl_delete_def_fd()`. The signatures use Samba's `vfs_handle_struct`, `struct smb_filename`, `files_struct`, `SMB_ACL_TYPE_T`, and `SMB_ACL_T` types.

Control flow: the header has no runtime control flow. It establishes the contract that file ACL operations can be called either by pathname-style `struct smb_filename` or by an open FSP, with implementation details hidden in the C file.

State and persistence: no state is declared. Persistent ACL effects occur only through the implementation's calls to HP-UX `acl()`.

Dependencies and integration points: depends on Samba core type declarations being included before or through the C file. It is included by `vfs_hpuxacl.c` and should match the VFS function table assignments in that file.

Risks and test signals: prototype drift is the main risk, because the C file uses both path-oriented and FSP-oriented wrappers. Compile testing on HP-UX is the key signal, followed by ABI checks that all declarations match Samba's current VFS callback signatures.
