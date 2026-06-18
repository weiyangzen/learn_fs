# sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_setgroups.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_setgroups.c

Purpose: Demonstrates replacing a user's global/domain group list with `NetUserSetGroups()`.

Important APIs/types/functions: Allocates `GROUP_USERS_INFO_0` or `_1` arrays through `NetApiBufferAllocate()` and submits member count to `NetUserSetGroups()`.

Control flow: Parses hostname, username, level, and group tokens, allocates the level-specific array, fills group names and optional attributes, calls the API, frees the buffer, and exits.

State and persistence behavior: Replaces persistent user group membership.

Dependencies and integration points: Verified by `user_getgroups` and group membership examples.

Risks: Destructive replacement can remove required memberships. Level 1 expects name/attribute pairs and parsing is positional.

Test signals: Set memberships for a disposable user and compare exactly with `user_getgroups`.
