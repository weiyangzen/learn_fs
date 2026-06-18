# sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_add.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_add.c

Purpose: Demonstrates creating a global/domain group with `NetGroupAdd()`.

Important APIs/types/functions: Uses `GROUP_INFO_1` with name and comment and passes level 1 plus `parm_err`.

Control flow: Parses hostname, group name, and optional comment, initializes `GROUP_INFO_1`, calls `NetGroupAdd()`, reports context error strings, then frees context and popt state.

State and persistence behavior: Creates persistent group state on the target server/domain.

Dependencies and integration points: Part of the group administration example suite with adduser, setinfo, enum, and delete.

Risks: No client-side validation of group naming rules or duplicate handling beyond server error. Requires suitable credentials.

Test signals: Add a test group, query it with `group_getinfo`, then remove it with `group_del`.
