<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_afsacl.c -->
# sources/user-network-fs/samba/source3/modules/vfs_afsacl.c

## Purpose
This VFS module converts between AFS ACL strings and Windows NT security descriptors. It lets Samba expose and set AFS directory ACLs through Windows ACL interfaces while preserving unmapped AFS principals where possible.

## Important APIs, Types, And Functions
Core types are `struct afs_ace`, `struct afs_acl`, and `struct afs_iob`. Helpers cover ACL allocation/freeing, parsing/unparsing AFS ACL text, ACE merge/clone, AFS-to-NT and NT-to-AFS rights conversion, file/dir ACL splitting and merging, SID/name mapping, AFS pioctl get/set, and unknown ACE preservation. VFS entry points are `afsacl_connect`, `afsacl_fget_nt_acl`, `afsacl_fset_nt_acl`, and `afsacl_sys_acl_blob_get_fd`.

## Control Flow
Connect calls the next VFS module and reads the `afsacl:space` replacement character. Get reads the AFS ACL with `afs_syscall(AFSCALL_PIOCTL, VIOCGETAL)`, parses positive/negative ACE lines, maps known AFS system names and PTS names to SIDs, converts rights into Windows ACE masks, and builds a security descriptor with owner/group from stat data. Set identifies the directory whose AFS ACL should be modified, reads the old ACL, splits it into directory and file rights, converts the incoming DACL into a new AFS dir or file ACL depending on object type and `afsacl:fileacls`, merges dir/file ACLs back together, preserves unknown old ACEs, unparses the ACL string, and writes it with `VIOCSETAL`.

## State And Persistence
AFS ACLs are durable state in the AFS filesystem and are accessed through pioctl syscalls. Module-global `space_replacement` and `sidpts` affect name parsing/mapping. Temporary ACL structures are talloc-managed within helper-owned contexts.

## Dependencies And Integration Points
The module depends on AFS headers/syscalls, Samba security/SID/passdb/name lookup, stat/VFS operations, loadparm, and the SMB VFS NT ACL hooks. It maps AFS special names such as `system:administrators`, `system:anyuser`, `system:authuser`, and `system:backup` to built-in or well-known SIDs.

## Risks
AFS ACLs have a different model from Windows ACLs; deny ACEs, inheritance, and file ACL behavior are approximated. `unparse_afs_acl` has a TODO about string length checks but uses bounded `strlcat` against `MAXSIZE`. Unknown principal preservation is best-effort. The `sidpts` mode changes whether PTS users/groups are represented as SIDs. `afsacl_sys_acl_blob_get_fd` returns `ENOSYS`, limiting hash validation integrations.

## Test Signals
Useful tests require an AFS environment: parse/unparse round trips, known system-name mapping, SID PTS mode, file versus directory ACL conversion, `afsacl:fileacls` modes `yes/no/ignore`, unknown ACE preservation, `VIOCGETAL`/`VIOCSETAL` failure handling, and Windows ACL get/set through SMB clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_afsacl.c -->
