# sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_setinfo.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_setinfo.c

Purpose: Demonstrates updating share metadata with `NetShareSetInfo()`.

Important APIs/types/functions: Supports level 1004 through `SHARE_INFO_1004` to set a share remark/comment.

Control flow: Parses hostname, share name, level, and comment value, fills the structure, calls `NetShareSetInfo()`, reports `parm_err` failures, and cleans up.

State and persistence behavior: Mutates persistent share configuration on the remote server.

Dependencies and integration points: Paired with `share_getinfo` level 1/2/501-style comment verification.

Risks: Only level 1004 is handled. Missing comment input can leave NULL data.

Test signals: Set a disposable share comment and verify via `share_getinfo` and `share_enum`.
