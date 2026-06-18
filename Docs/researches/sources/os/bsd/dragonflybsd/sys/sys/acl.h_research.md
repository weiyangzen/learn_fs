# File Research: sources/os/bsd/dragonflybsd/sys/sys/acl.h

Read completely: 142 lines.

This header defines the POSIX.1e ACL user/kernel interface.

Key contents:
- ACL scalar types: `acl_type_t`, `acl_tag_t`, and `acl_perm_t`.
- `struct acl_entry` and `struct acl`, with `ACL_MAX_ENTRIES` set to 32.
- ACL tag constants for owner/user/group/mask/other entries.
- ACL type constants for access, default, AFS, CODA, and NTFS ACLs.
- Permission constants for read/write/execute.
- Userland syscall-entry prototypes and libc ACL helper prototypes.

Security/reliability notes:
- No executable logic. The comments warn that raw syscalls require strict ACL entry ordering; most callers should use library helpers.
- Structure layout and maximum entry count are ABI-sensitive.
