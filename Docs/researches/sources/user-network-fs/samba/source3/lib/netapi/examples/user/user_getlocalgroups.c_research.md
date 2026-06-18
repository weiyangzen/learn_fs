# sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getlocalgroups.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getlocalgroups.c

Purpose: Demonstrates retrieving local groups containing a user with `NetUserGetLocalGroups()`.

Important APIs/types/functions: Supports level 0 using `LOCALGROUP_USERS_INFO_0`; accepts flags and resume paging.

Control flow: Parses hostname, username, level, and optional flags, loops through pages, prints local group names, frees buffers, and handles final status.

State and persistence behavior: Read-only membership query.

Dependencies and integration points: Verifies local group membership operations from the user perspective.

Risks: Only level 0 is printed. Flag semantics are server-defined and lightly validated.

Test signals: Add a user to local groups, query with relevant flags, and compare with `localgroup_getmembers`.
