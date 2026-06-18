# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netlocalgroup.c

Purpose: destructive integration tests for local group NetAPI operations. It covers local group creation, enumeration, get-info levels, rename through set-info, delete, and negative lookup after delete.

Important APIs/functions: `test_netlocalgroupenum` loops over `NetLocalGroupEnum` levels 0 and 1 and searches returned `LOCALGROUP_INFO_*` entries for a group name. `netapitest_localgroup` drives `NetLocalGroupAdd`, `NetLocalGroupGetInfo`, `NetLocalGroupSetInfo`, `NetLocalGroupDel`, and post-delete `NetLocalGroupGetInfo`.

Control flow: fixed names `torture_test_localgroup` and `torture_test_localgroup2` are deleted first. The test adds level 0 group data, enumerates levels 0/1, queries levels 0/1/1002 while tolerating status 124, renames the group with level 0 set-info, verifies the old name cannot be deleted, queries the new name, deletes it, and verifies get-info no longer succeeds.

State and persistence: mutates the target's local alias database by creating, renaming, and deleting local groups. Temporary buffers are released through `NetApiBufferFree`.

Dependencies/integration: depends on public local group structs/prototypes and shared macros. It requires administrative rights on the target server.

Risks: no local group membership APIs are exercised despite being declared in `netapi.h`. Fixed names are unsafe for parallel test runs. If rename succeeds but later assertions fail, cleanup only deletes the new name along the main path; failure in the middle can leave objects until the next run's initial cleanup.

Test signals: add tests for `NetLocalGroupAddMembers`, `DelMembers`, `GetMembers`, and `SetMembers`, use unique names per run, verify level 1002 comment behavior, and run post-failure cleanup checks against the target SAM.
