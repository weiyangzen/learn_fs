# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_support.c

Provides internal support routines for POSIX.1e ACL handling. It includes ACL comparison, POSIX entry sorting, POSIX validity checks, permission string conversion, raw entry insertion, old ACL type translation, and whitespace helpers.

Important functions:
- `_acl_differs()` compares brand-compatible ACLs entry-by-entry, including tag, id, permissions, entry type, and flags.
- `_posix1e_acl_sort()` sorts ACL entries into kernel validation order.
- `_posix1e_acl_check()` validates sorted POSIX ACLs: permission bits, tag order, required single owner/group/other entries, optional single mask, and monotonically increasing named user/group ids.
- `_posix1e_acl_perm_to_string()` and `_posix1e_acl_string_to_perm()` convert between `rwx` text and permission bits.
- `_acl_type_unold()` maps legacy access/default ACL type constants to current constants.

The file mirrors kernel ACL validation expectations for userland preflight. It relies on `_acl_brand()` and `_entry_brand()` being meaningful, and uses `assert()` heavily for internal invariants.
