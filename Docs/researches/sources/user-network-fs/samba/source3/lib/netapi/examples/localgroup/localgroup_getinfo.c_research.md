# sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_getinfo.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_getinfo.c

Purpose: Demonstrates querying local group details with `NetLocalGroupGetInfo()`.

Important APIs/types/functions: Handles `LOCALGROUP_INFO_0`, `_1`, and `_1002` for name/comment data.

Control flow: Parses hostname, group, and level, calls the API, switches on level to print fields, frees the result buffer, and cleans up.

State and persistence behavior: Read-only remote metadata query.

Dependencies and integration points: Used to validate local group add/setinfo operations.

Risks: Unsupported levels are not described. Output is sample/debug oriented.

Test signals: Query a known group at levels 0, 1, and 1002 and compare comment changes.
