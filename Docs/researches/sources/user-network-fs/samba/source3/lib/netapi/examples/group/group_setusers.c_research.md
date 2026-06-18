# sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_setusers.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_setusers.c

Purpose: Demonstrates replacing a global/domain group's user list with `NetGroupSetUsers()`.

Important APIs/types/functions: Allocates `GROUP_USERS_INFO_0` or `_1` arrays with `NetApiBufferAllocate()`, fills names and optional attributes, then calls `NetGroupSetUsers()`.

Control flow: Parses hostname, group, level, and member tokens. It computes entry count, allocates a NetAPI-owned buffer, populates entries from positional args, submits the replacement, frees the buffer, and cleans up.

State and persistence behavior: Replaces persistent remote membership state for the target group.

Dependencies and integration points: Uses NetAPI buffer allocator because structures are passed to NetAPI calls.

Risks: Destructive replacement can remove existing members. Input parsing assumes pairs for level 1. No rollback on partial server-side failure.

Test signals: Set a disposable group to a known membership list and verify exactly with `group_getusers`.
