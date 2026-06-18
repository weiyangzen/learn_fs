# sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_getinfo.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_getinfo.c

Purpose: Demonstrates querying one global/domain group with `NetGroupGetInfo()`.

Important APIs/types/functions: Handles `GROUP_INFO_0`, `_1`, `_2`, and `_3`, including SID conversion for level 3.

Control flow: Parses hostname, group name, and level, calls `NetGroupGetInfo()`, switches on the requested level to print name/comment/id/attributes/SID, then frees the result.

State and persistence behavior: Read-only remote group metadata query.

Dependencies and integration points: Used after create or modify examples to verify group state.

Risks: Unsupported levels produce little feedback. Output formatting is demonstration-oriented, not machine stable.

Test signals: Query a known group at levels 0-3 and verify fields match enumeration output.
