# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_acl_posix1e.c

## Summary
Implements common POSIX.1e ACL utility routines for FreeBSD filesystems, including access checks, mode conversion, ACL validation, and default-ACL mode composition.

## Main Responsibilities
- Evaluates vnode access requests using POSIX.1e ACL semantics.
- Converts inode mode bits to POSIX.1e ACL permissions and base ACL entries.
- Converts POSIX.1e access ACLs back to mode bits.
- Performs syntactic validation of POSIX.1e ACL shape.
- Applies a default ACL to a requested creation mode.

## Key APIs
- `vaccess_acl_posix1e()`: ACL-aware access check.
- `acl_posix1e_mode_to_perm()`: converts mode bits for `ACL_USER_OBJ`, `ACL_GROUP_OBJ`, or `ACL_OTHER`.
- `acl_posix1e_mode_to_entry()`: builds a base ACL entry from uid/gid/mode.
- `acl_posix1e_perms_to_mode()`: derives mode bits from three base entries.
- `acl_posix1e_acl_to_mode()`: derives mode bits from a full access ACL, using `ACL_MASK` for group bits when present.
- `acl_posix1e_check()`: validates ACL count, required tags, ids, mask presence, and permission bits.
- `acl_posix1e_newfilemode()`: combines requested creation mode with a default ACL.

## Important Behavior
Access checking follows POSIX.1e matching order: owner object, named user, group class best-match, then other. `ACL_MASK` gates named users, group object, and named groups but not owner or other. Group matching is best-match, so the code first records whether any group entry matched before deciding whether to fall back to `ACL_OTHER`.

Privilege grants are computed before ACL evaluation but used only after a matching DAC path fails. Directory execute maps to lookup privilege; regular-file execute privilege is only considered when at least one execute bit is set in the ACL-derived mode.

`acl_posix1e_acl_to_mode()` panics on malformed ACLs with missing base entries or unknown tags, so callers are expected to validate externally before using it on untrusted ACLs.

`acl_posix1e_check()` requires exactly one `ACL_USER_OBJ`, one `ACL_GROUP_OBJ`, and one `ACL_OTHER`; allows zero or one `ACL_MASK`; and requires a mask if any named user or named group entries exist. It normalizes base/mask entry ids to `ACL_UNDEFINED_ID`.

## Dependencies
Uses FreeBSD ACL, vnode access mode, credential/group membership, privilege, module, and VFS headers.

## Risks
The access checker contains comments noting that privilege selection is approximate and sometimes falls back to first-match behavior. `acl_posix1e_check()` mutates some entry ids while validating, which callers must tolerate. Malformed ACLs passed to conversion helpers can panic.
