# sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_setinfo.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_setinfo.c

Purpose: Demonstrates updating global/domain group metadata with `NetGroupSetInfo()`.

Important APIs/types/functions: Supports levels 0, 1, 2, 3, 1002, and 1005 over `GROUP_INFO_*` structures and `parm_err`.

Control flow: Parses hostname, group, level, and value fields, fills the level-specific structure with new name/comment/attributes as applicable, calls `NetGroupSetInfo()`, and reports failures.

State and persistence behavior: Mutates remote group metadata.

Dependencies and integration points: Pairs with `group_getinfo` for validation and with domain group administration APIs.

Risks: Positional input is level-dependent and lightly validated. Rename/comment/attribute semantics vary by server support.

Test signals: Change a disposable group's comment/name where supported and verify through `group_getinfo`.
