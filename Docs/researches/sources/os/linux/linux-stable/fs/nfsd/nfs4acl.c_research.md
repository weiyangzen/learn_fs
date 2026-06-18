# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4acl.c

## Summary
Common NFSv4 ACL conversion logic between NFSv4 ACE lists and Linux POSIX ACLs.

## Main APIs
- `nfsd4_get_nfs4_acl()` converts inode access/default POSIX ACLs to an NFSv4 ACL.
- `nfsd4_acl_to_attr()` converts an NFSv4 ACL into `nfsd_attrs` POSIX ACL fields.
- `nfs4_acl_bytes()`, `nfs4_acl_get_whotype()`, `nfs4_acl_write_who()`.
- `sort_pacl_range()` supports POSIX ACL validation ordering.

## Behavior
POSIX-to-NFSv4 conversion emits deny/allow ACEs for owner, named users, group, named groups, and everyone, with special inheritance flags for default ACLs. NFSv4-to-POSIX conversion processes ALLOW and DENY ACEs into accumulated per-subject allow/deny masks, splits effective and default ACL state, copies missing owner/group/other entries into default ACLs, builds POSIX ACLs, and sorts named entries.

## Risks
The NFSv4-to-POSIX path is intentionally restrictive and rejects unsupported ACE types/flags. Permission mapping is lossy between richer NFSv4 ACE semantics and POSIX ACLs. Internal state arrays allocate worst-case user/group entries based on ACE count.
