# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_acl.c

## Role

Implements common FreeBSD ACL syscall plumbing and vnode dispatch for POSIX.1e/NFSv4-era ACL operations. Type-specific ACL semantics live elsewhere; this file translates user requests into `VOP_SETACL`, `VOP_GETACL`, and `VOP_ACLCHECK`.

## Main Responsibilities

- Supports ACL get/set/delete/check operations by path, link, and file descriptor.
- Converts legacy `struct oldacl` layouts into modern `struct acl`.
- Preserves old syscall ABI behavior for `ACL_TYPE_ACCESS_OLD` and `ACL_TYPE_DEFAULT_OLD`.
- Performs user copyin/copyout validation.
- Applies MAC framework checks before vnode ACL operations.
- Wraps mutating ACL operations in VFS write transactions.

## ACL Compatibility Handling

The file handles pre-NFSv4 ACL ABI compatibility:

- `acl_copy_oldacl_into_acl()` converts legacy entries into a modern `struct acl`.
- `acl_copy_acl_into_oldacl()` converts back if the result fits `OLDACL_MAX_ENTRIES`.
- `acl_copyin()` decides whether user memory contains `oldacl` or modern `acl` based on ACL type.
- `acl_copyout()` checks user `acl_maxcnt` for modern ACLs before copying out.
- `acl_type_unold()` maps old ACL type constants to modern `ACL_TYPE_ACCESS` or `ACL_TYPE_DEFAULT`.

This means old libc binaries and newer kernels can interoperate without duplicate syscall implementations.

## Vnode Operation Wrappers

The central wrappers are:

- `vacl_set_acl()`: allocates kernel ACL storage, copies in user ACL, starts a write transaction, locks vnode exclusive, checks MAC policy, then calls `VOP_SETACL()`.
- `vacl_get_acl()`: locks vnode exclusive, checks MAC policy, calls `VOP_GETACL()`, then copies the ACL back to user memory.
- `vacl_delete()`: starts a write transaction, locks vnode exclusive, checks MAC policy, and deletes by calling `VOP_SETACL(..., NULL, ...)`.
- `vacl_aclcheck()`: copies in ACL and invokes `VOP_ACLCHECK()`.

Mutating operations use `vn_start_write()` / `vn_finished_write()` to coordinate with mounts and write suspension.

## Syscall Entry Points

Path and link variants use `namei()`:

- `sys___acl_get_file()`
- `sys___acl_get_link()`
- `sys___acl_set_file()`
- `sys___acl_set_link()`
- `sys___acl_delete_file()`
- `sys___acl_delete_link()`
- `sys___acl_aclcheck_file()`
- `sys___acl_aclcheck_link()`

Path helpers differ mostly by `FOLLOW` versus `NOFOLLOW`.

File descriptor variants use Capsicum-aware vnode lookup:

- `sys___acl_get_fd()` requires `CAP_ACL_GET`.
- `sys___acl_set_fd()` requires `CAP_ACL_SET`.
- `sys___acl_delete_fd()` requires `CAP_ACL_DELETE`.
- `sys___acl_aclcheck_fd()` requires `CAP_ACL_CHECK`.

`getvnode_path()` is used where path-style rights are relevant; `getvnode()` is used for direct fd operations.

## Security and Auditing

- Uses `AUDIT_ARG_VALUE()`, `AUDIT_ARG_VNODE1()`, and `AUDIT_ARG_FD()` to capture syscall audit data.
- MAC hooks gate get, set, and delete operations:
  - `mac_vnode_check_getacl()`
  - `mac_vnode_check_setacl()`
  - `mac_vnode_check_deleteacl()`
- Capsicum capabilities are enforced before fd-based vnode access.

## Memory Management

- Defines `M_ACL`.
- `acl_alloc()` allocates a `struct acl` and initializes `acl_maxcnt`.
- `acl_free()` releases ACL memory.
- Most wrappers allocate temporary kernel ACLs with `M_WAITOK`; syscall-facing code keeps user pointers out of filesystem-specific VOPs.

## Research Relevance

This is a compact VFS syscall adapter. It shows FreeBSD’s pattern for translating user ABI structures into kernel-private structures, enforcing Capsicum/MAC/audit policy, and routing filesystem-specific behavior through vnode operations. For filesystem research, it is useful as the common front door through which UFS/ZFS/NFS or other filesystems expose ACL support to userland.
