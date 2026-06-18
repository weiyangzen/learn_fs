# sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_add.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_add.c

Purpose: Demonstrates creating a share with `NetShareAdd()`.

Important APIs/types/functions: Uses `SHARE_INFO_2` with netname, type, remark, permissions, max/current uses, path, and password fields.

Control flow: Parses hostname, share name, path, and optional comment, fills `SHARE_INFO_2`, calls level 2 `NetShareAdd()`, reports `parm_err` failures, and exits.

State and persistence behavior: Creates persistent share configuration on the target server.

Dependencies and integration points: Share administration suite with enum/get/set/delete.

Risks: No path existence or permission validation before RPC. Password field is set NULL; share type defaults are sample-specific.

Test signals: Add a disposable share, query with `share_getinfo`, enumerate, then delete.
