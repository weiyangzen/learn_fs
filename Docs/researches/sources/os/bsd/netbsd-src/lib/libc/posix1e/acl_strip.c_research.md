# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_strip.c

Implements `acl_strip_np()` and `acl_is_trivial_np()` for POSIX.1e and NFSv4 ACLs. POSIX ACL stripping keeps only `ACL_USER_OBJ`, `ACL_GROUP_OBJ`, and `ACL_OTHER`, optionally recalculating `ACL_MASK` if a mask existed. NFSv4 stripping derives mode bits from the ACL with `__acl_nfs4_sync_mode_from_acl()` and rebuilds a trivial ACL with `__acl_nfs4_trivial_from_mode_libc()`.

Key dependencies are brand helpers from `acl_support.h`, public ACL iteration/copy APIs, `acl_calc_mask()`, and kernel/shared NFSv4 ACL helpers declared in `sys/acl.h`. `acl_is_trivial_np()` treats a POSIX ACL with exactly three entries as trivial and compares NFSv4 ACLs against both normal and canonical-six trivial forms via `_acl_differs()`.

Important behavior: invalid or unknown ACL brands return `EINVAL`; allocation failures return `NULL`, sometimes with `ENOMEM`. The POSIX strip helper duplicates the input first, then creates a new ACL, so input ACL ordering and entry brands are expected to be valid.
