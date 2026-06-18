# sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getgroups.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getgroups.c

Purpose: Demonstrates retrieving global/domain groups for a user with `NetUserGetGroups()`.

Important APIs/types/functions: Supports levels 0 and 1 using `GROUP_USERS_INFO_0` and `_1`, with attributes at level 1.

Control flow: Parses hostname, username, and level, loops through result pages, prints group names/attributes, frees buffers, and handles errors.

State and persistence behavior: Read-only membership query.

Dependencies and integration points: Verifies `user_setgroups`, `group_adduser`, and `group_deluser`.

Risks: Only global group memberships are represented; local groups use a separate API.

Test signals: Add/set user group memberships and confirm output reflects changes.
