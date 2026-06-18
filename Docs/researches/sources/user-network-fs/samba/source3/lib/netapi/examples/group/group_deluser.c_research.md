# sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_deluser.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_deluser.c

Purpose: Demonstrates removing a user from a global/domain group with `NetGroupDelUser()`.

Important APIs/types/functions: Calls `NetGroupDelUser(hostname, groupname, username)`.

Control flow: Initializes, parses common options and positional hostname/group/user arguments, calls the API, reports context error strings, and releases resources.

State and persistence behavior: Mutates remote group membership only.

Dependencies and integration points: Mirrors `group_adduser` and is verified by `group_getusers`.

Risks: No pre-check that the member exists in the group. Server may distinguish nonexistent users, groups, and absent membership.

Test signals: Add then remove a disposable user membership and enumerate members after each step.
