# sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getinfo.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_getinfo.c

Purpose: Demonstrates querying detailed user account information with `NetUserGetInfo()`.

Important APIs/types/functions: Handles many levels, including `USER_INFO_0/1/2/3/4/10/11/20/23`. Prints password age, privilege, home/script/profile fields, flags, logon times, logon hours, counts, SIDs, and primary group data where present.

Control flow: Parses hostname, username, and level, calls the API, switches on level to cast and print fields, frees the returned buffer, and cleans up.

State and persistence behavior: Read-only account metadata query.

Dependencies and integration points: Primary verifier for user add/setinfo/modals/group operations.

Risks: Some levels expose sensitive fields such as password placeholders, workstation restrictions, and account policy data. Large switch must stay aligned with NetAPI structures.

Test signals: Query a disposable user across all supported levels and compare selected fields after `user_setinfo`.
