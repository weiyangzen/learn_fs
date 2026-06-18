# sources/test-tools/strace/bundled/linux/include/uapi/linux/xattr.h

## Purpose
Defines Linux extended-attribute userspace constants used by filesystem, security, and strace xattr decoders: set flags, an extensible argument structure, namespace prefixes, and standard security/system attribute names.

## Important APIs, Types, and Functions
Read coverage: 96 lines and 3294 bytes. When `__UAPI_DEF_XATTR` permits kernel definitions, it exports `XATTR_CREATE` and `XATTR_REPLACE` for setxattr-style calls and `struct xattr_args` containing an aligned userspace value pointer, value size, and flags. Namespace prefix macros cover `os2.`, `osx.`, `btrfs.`, `gnu.`, `security.`, `system.`, `trusted.`, and `user.`, with matching length macros. Security names include EVM, IMA, SELinux, SMACK variants, AppArmor, file capabilities, and BPF LSM prefix naming. System ACL names include `system.posix_acl_access` and `system.posix_acl_default`.

## Control Flow
The header has no runtime flow. Userspace passes the flags to `setxattr`/`lsetxattr`/`fsetxattr` or related syscalls, and kernel/filesystem/security code uses the namespace prefixes to route access control and interpretation. `struct xattr_args` is suitable for newer extensible syscall payloads that need a stable pointer/size/flag tuple.

## State and Persistence Behavior
Extended attributes are persisted by filesystems or security subsystems on inodes. This header defines the names and flags that describe those persisted key/value entries; it does not store state itself. Names in `security.*`, `system.*`, `trusted.*`, and `user.*` carry policy-sensitive state such as LSM labels, IMA/EVM metadata, POSIX ACLs, and file capabilities.

## Dependencies and Integration Points
Direct includes are `<linux/libc-compat.h>` and `<linux/types.h>`. The libc-compat guard avoids conflicting definitions when libc supplies the xattr API. In strace this header supports symbolic decoding of xattr flags and well-known names. It integrates with VFS xattr syscalls, filesystems, SELinux, SMACK, AppArmor, IMA/EVM, file capabilities, BPF LSM, POSIX ACLs, and backup/archive tools.

## Risks and Edge Cases
Namespace semantics differ: `trusted.*` requires privilege, `security.*` is LSM-controlled, `system.*` may be filesystem-managed, and `user.*` depends on mount/filesystem policy. Incorrect create/replace flag decoding changes error expectations. `struct xattr_args.value` is an aligned 64-bit user pointer for compat safety, so strace must decode it as an address rather than inline data. Security attribute values may be sensitive.

## Test Signals
Test signals include strace xattr syscall decoding with no flags, `XATTR_CREATE`, `XATTR_REPLACE`, known security/system/user names, 32-bit compat pointer layout for `struct xattr_args`, filesystem round-trips on ext4/xfs/btrfs/tmpfs where supported, and permission/error checks for security and trusted namespaces.
