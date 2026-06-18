# sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_add.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_add.c

Purpose: Demonstrates creating a user account with `NetUserAdd()`.

Important APIs/types/functions: Uses `USER_INFO_1` with name, password, privilege, home directory, comment, flags, and script path. Sets flags such as `UF_SCRIPT`.

Control flow: Parses hostname, username, password, and optional comment, fills the structure, calls level 1 `NetUserAdd()`, reports `parm_err` failures, and exits.

State and persistence behavior: Creates persistent user account state on the target server/domain.

Dependencies and integration points: User administration suite with get/set/groups/delete examples.

Risks: Password is passed on command line and may be exposed. Defaults are sample-oriented and not policy-aware.

Test signals: Add a disposable user, query with `user_getinfo`, then remove with `user_del`.
