# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_acl.c

## Purpose
Implements ACL syscall glue and vnode wrappers for getting, setting, deleting, and validating filesystem ACLs, including compatibility conversion between old POSIX.1e ACL layout and newer ACL structures.

## Main Interfaces
- `acl_copy_oldacl_into_acl`, `acl_copy_acl_into_oldacl`: convert old/new ACL structures.
- `acl_copyin`, `acl_copyout`, `acl_type_unold`: select compatibility layout based on ACL type.
- `vacl_set_acl`, `vacl_get_acl`, `vacl_delete`, `vacl_aclcheck`: lock vnodes and call `VOP_SETACL`, `VOP_GETACL`, and `VOP_ACLCHECK`.
- Path syscalls: `sys___acl_get_file`, `sys___acl_get_link`, `sys___acl_set_file`, `sys___acl_set_link`, `sys___acl_delete_file`, `sys___acl_delete_link`, `sys___acl_aclcheck_file`, `sys___acl_aclcheck_link`.
- FD syscalls: `sys___acl_get_fd`, `sys___acl_set_fd`, `sys___acl_delete_fd`, `sys___acl_aclcheck_fd`.
- Kernel path helpers: `kern___acl_get_path`, `kern___acl_set_path`, `kern___acl_delete_path`, `kern___acl_aclcheck_path`.
- `acl_alloc`, `acl_free`: allocate initialized ACL buffers.

## State And Control Flow
Syscalls resolve either a user path with follow/no-follow semantics or a file descriptor to a vnode, then call a common `vacl_*` helper. ACL payloads are copied into temporary kernel ACL buffers before vnode operations, and copied back out after successful gets. Old ACL types are translated to modern access/default types before invoking filesystem vnode operations.

## Dependencies And Integration
Uses namei simple path lookup, descriptor-to-vnode lookup, vnode locks, filesystem ACL vnode operations, `copyin`/`copyout`, credentials from the calling LWP, and NetBSD ACL allocation helpers.

## Risks And Edge Cases
- Compatibility depends on ACL type values: old binaries using old access/default types get structure conversion, while all other types expect `acl_maxcnt == ACL_MAX_ENTRIES`.
- Path variants differ only in symlink-following policy, so callers must choose the correct entry point.
- Filesystem-specific ACL validation and storage are delegated to VOPs; this file only handles syscall marshalling and locking.
- `vacl_aclcheck` intentionally performs no vnode lock, matching the inherited comment that vnode state auditing is limited there.

## Filesystem Relevance
High. This is the VFS-facing ACL syscall layer for filesystem permission metadata.
