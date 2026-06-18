# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_acl_posix1e.c

Read completely: 341 lines.

Provides shared POSIX.1e ACL utility routines for filesystems. It converts between inode mode bits and ACL entries, validates POSIX.1e ACL structure, and combines creation modes with default ACLs for new files.

Mode-to-ACL helpers:
- `acl_posix1e_mode_to_perm()` maps `S_IRWXU`, `S_IRWXG`, or `S_IRWXO` bits to `ACL_READ`, `ACL_WRITE`, and `ACL_EXECUTE` according to the requested tag.
- `acl_posix1e_mode_to_entry()` builds a base ACL entry for `ACL_USER_OBJ`, `ACL_GROUP_OBJ`, or `ACL_OTHER`, filling the owner uid, group gid, or undefined ID as appropriate.
- Invalid tags are reported with `printf()` and return an empty/undefined entry rather than panicking.

ACL-to-mode helpers:
- `acl_posix1e_perms_to_mode()` converts three relevant ACL entries back into user/group/other mode bits.
- `acl_posix1e_acl_to_mode()` finds `ACL_USER_OBJ`, `ACL_GROUP_OBJ`, `ACL_OTHER`, and optional `ACL_MASK` entries in a complete ACL.
- If `ACL_MASK` exists, its permissions replace group bits in the resulting mode, matching POSIX.1e behavior.
- Missing required base entries or unknown tags cause `panic()`, reflecting the expectation that callers validate ACLs first.

Validation:
- `acl_posix1e_check()` verifies `acl_cnt <= ACL_MAX_ENTRIES`.
- It requires exactly one `ACL_USER_OBJ`, exactly one `ACL_GROUP_OBJ`, exactly one `ACL_OTHER`, and zero or one `ACL_MASK`.
- If any named `ACL_USER` or `ACL_GROUP` entries are present, exactly one `ACL_MASK` must be present.
- Named user/group entries must have defined IDs; base entries and mask are forced to `ACL_UNDEFINED_ID` before checking.
- Permissions must be limited to `ACL_PERM_BITS`, and tags outside the POSIX.1e set are rejected with `EINVAL`.

New-file mode composition:
- `acl_posix1e_newfilemode()` preserves non-ACL mode bits through `ACL_PRESERVE_MASK`.
- It applies the current policy that a permission bit must be present both in the requested creation mode and in the default ACL-derived mode to survive.
- It reconstructs affected permission bits with `ACL_OVERRIDE_MASK & cmode & acl_posix1e_acl_to_mode(dacl)`.

Risks and notes:
- `acl_posix1e_check()` mutates `ae_id` for base and mask entries while validating, which is surprising for a function named as a checker.
- `acl_posix1e_acl_to_mode()` panics on malformed ACLs; callers must run validation before using it on untrusted ACL data.
- The validator explicitly does not check uniqueness of named user/group qualifier IDs.
- Default ACL composition does not take a separate process umask argument here; comments note that may eventually be pushed into per-filesystem code.
