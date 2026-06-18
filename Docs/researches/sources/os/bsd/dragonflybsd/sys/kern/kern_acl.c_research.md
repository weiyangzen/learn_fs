# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_acl.c

## Summary
Implements generic syscall wrappers for filesystem ACL operations. It handles path/fd to vnode conversion and user/kernel ACL copying, while filesystem-specific semantics live in VOP ACL methods.

## Main Responsibilities
- Wraps `VOP_SETACL`, `VOP_GETACL`, and `VOP_ACLCHECK`.
- Implements path-based ACL syscalls: `__acl_get_file`, `__acl_set_file`, `__acl_delete_file`, `__acl_aclcheck_file`.
- Implements fd-based ACL syscalls: `__acl_get_fd`, `__acl_set_fd`, `__acl_delete_fd`, `__acl_aclcheck_fd`.

## Important Behavior
Path syscalls use `nlookup` with `NLC_FOLLOW`, then `cache_vref` to obtain a vnode reference. FD syscalls use `holdvnode`. Set/delete operations lock the vnode exclusive; get/check rely on the VOP path.

User ACL data is copied into kernel memory before set/check and copied back after get.

## Risks
`vacl_delete()` ignores its `type` argument and calls `VOP_SETACL(vp, ACL_TYPE_DEFAULT, 0, ucred)`, so delete behavior is hardwired to default ACLs in this file. ACL permission and semantic validation are delegated to individual filesystems.
