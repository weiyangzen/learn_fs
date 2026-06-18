# sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_add.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_add.c

Purpose: Demonstrates creating a local group with `NetLocalGroupAdd()`.

Important APIs/types/functions: Supports levels 0 and 1 using `LOCALGROUP_INFO_0` and `LOCALGROUP_INFO_1` with optional comment and `parm_err`.

Control flow: Parses hostname, group name, level, and optional comment; fills the matching structure; calls the API; reports errors and cleanup.

State and persistence behavior: Creates persistent local group state on the target server.

Dependencies and integration points: Local-group administration suite with membership and info examples.

Risks: Level-dependent positional parsing is minimal. Requires administrative rights.

Test signals: Add a disposable local group, query with `localgroup_getinfo`, delete with `localgroup_del`.
