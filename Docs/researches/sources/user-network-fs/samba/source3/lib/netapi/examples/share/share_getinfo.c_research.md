# sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_getinfo.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_getinfo.c

Purpose: Demonstrates querying one share through `NetShareGetInfo()`.

Important APIs/types/functions: Handles levels 0, 1, 2, 501, and 1005 using corresponding `SHARE_INFO_*` structures.

Control flow: Parses hostname/share/level, calls the API, casts and prints level-specific netname/type/remark/permission/user/path/password/flags fields, frees the buffer, and exits.

State and persistence behavior: Read-only share metadata query.

Dependencies and integration points: Validation target for `share_add` and `share_setinfo`.

Risks: May print sensitive share password fields when present. Unsupported levels are not fully described.

Test signals: Query a disposable share at supported levels and compare with enumeration output.
