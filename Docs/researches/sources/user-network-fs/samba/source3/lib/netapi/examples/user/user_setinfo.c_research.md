# sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_setinfo.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_setinfo.c

Purpose: Demonstrates updating user account fields with `NetUserSetInfo()`.

Important APIs/types/functions: Supports many levels and parameter levels, including `USER_INFO_0`, `USER_INFO_1003`, `_1005`, `_1006`, `_1007`, `_1008`, `_1009`, `_1010`, `_1011`, `_1012`, `_1014`, `_1017`, `_1024`, `_1051`, `_1052`, and `_1053`.

Control flow: Parses hostname, username, level, and a value, fills the level-specific structure for password, privilege, home directory, comment, flags, script path, auth flags, full name, user comment, parameters, workstations, account expiration, max storage, logon server, country/code page, profile, home-drive, or password-expired fields, calls `NetUserSetInfo()`, reports errors, and cleans up.

State and persistence behavior: Mutates persistent user account properties on the target server/domain.

Dependencies and integration points: Main mutation counterpart to `user_getinfo`.

Risks: Security-sensitive fields are changed from minimally validated strings/integers. Some whole-structure levels are accepted but only small portions are populated, so parameter levels are safer.

Test signals: Update one field at a time on a disposable user and verify through `user_getinfo`; include policy rejection cases.
