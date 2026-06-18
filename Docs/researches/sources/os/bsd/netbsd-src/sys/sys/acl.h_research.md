# File Research: sources/os/bsd/netbsd-src/sys/sys/acl.h

Read completely: 440 lines.

Defines NetBSD ACL types, constants, kernel interfaces, private syscall interfaces, and userland ACL library prototypes for POSIX.1e and NFSv4 ACLs.

Core types and structures:
- Defines ACL scalar types: tags, permissions, entry types, flags, ACL type IDs, permsets, and flagsets.
- `ACL_MAX_ENTRIES` is 254 so the internal ACL structure fits one 4 KiB page.
- Kernel/private builds expose `struct oldacl_entry`, `struct oldacl`, `struct acl_entry`, `struct acl`, and libc's internal `struct acl_t_struct`.
- Non-private userland sees opaque `acl_t` and `acl_entry_t`.
- `struct oldacl` remains limited by `OLDACL_MAX_ENTRIES` for compatibility and POSIX.1e on-disk storage.

ACL constants:
- Defines POSIX.1e tags such as owner, named user, group, mask, other, and everyone.
- Defines NFSv4 entry types: allow, deny, audit, and alarm.
- Defines ACL type IDs for old access/default, current access/default, and NFSv4 ACLs.
- POSIX permission bits cover read/write/execute.
- NFSv4 permission bits cover data, named attributes, delete, ACL read/write, owner write, synchronize, and derived full/modify/read/write sets.
- Defines NFSv4 inheritance and audit flags.
- `ACL_UNDEFINED_ID` marks entries whose tag should not carry a uid/gid.

Kernel interfaces:
- Declares POSIX.1e mode/ACL conversion helpers, allocation/free helpers, NFSv4 mode sync/inheritance/triviality helpers, old/current ACL conversion helpers, and validation functions.
- Declares kernel ACL syscall helper entry points and vnode-level ACL helpers such as `vacl_set_acl`, `vacl_get_acl`, `vacl_aclcheck`, and `vacl_delete`.

User/private interfaces:
- `_ACL_PRIVATE` exposes raw `__acl_*` syscall wrappers and shared NFSv4 helpers used by libc.
- Public userland prototypes cover ACL creation, duplication, entry iteration, permission/flag mutation, text conversion, validation, file/fd/link get/set/delete calls, triviality checks, and ACL stripping.

Risks and notes:
- Increasing `ACL_MAX_ENTRIES` may require changing libc alignment assumptions.
- Changing `OLDACL_MAX_ENTRIES` would break pre-8.0 binary compatibility and POSIX.1e on-disk layout.
- Kernel code should use the VOP ACL type argument, not libc's internal ACL brand field.
