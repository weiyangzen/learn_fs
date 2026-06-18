# sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_getusers.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_getusers.c

Purpose: Demonstrates paged enumeration of users in a global/domain group with `NetGroupGetUsers()`.

Important APIs/types/functions: Supports levels 0 and 1 using `GROUP_USERS_INFO_0` and `GROUP_USERS_INFO_1`; level 1 prints membership attributes.

Control flow: Parses hostname/group/level, loops through result pages with a resume handle, prints member names and optional attributes, frees buffers, then reports final errors.

State and persistence behavior: Read-only membership query; no local persistence.

Dependencies and integration points: Verifies `group_adduser`, `group_deluser`, and `group_setusers` examples.

Risks: Only global group membership is represented; nested/local group semantics are server-defined.

Test signals: Compare output before and after membership mutation and exercise multi-page membership results.
