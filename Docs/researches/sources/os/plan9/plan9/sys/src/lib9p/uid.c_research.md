# File Research: sources/os/plan9/plan9/sys/src/lib9p/uid.c

This file implements simple permission checking for lib9p tree-backed files.

Key behavior:
- `hasperm` checks requested access bits against other, owner, and group permissions.
- Owner match is `strcmp(f->uid, uid) == 0`.
- Group match is simplified to `strcmp(f->gid, uid) == 0`.
- Returns true when any applicable permission class satisfies the requested mask.

Notable details:
- The comment states the simplification: each user is assumed to be the leader/member of her own group.
- Permissions are additive: matching owner or group ORs those permission bits with the already-checked other bits.
