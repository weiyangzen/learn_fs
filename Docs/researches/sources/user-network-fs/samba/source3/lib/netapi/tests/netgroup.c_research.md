# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netgroup.c

Purpose: destructive integration tests for global/domain group NetAPI operations. It creates test groups and users, exercises enumeration, get/set info, membership add/delete/set, and cleanup.

Important APIs/functions: helpers `test_netgroupenum`, `test_netgroupgetusers`, and `test_netgroupsetusers` cover `NetGroupEnum`, `NetGroupGetUsers`, and `NetGroupSetUsers` levels 0/1 as applicable. `netapitest_group` drives `NetGroupAdd`, duplicate-add failure, `NetGroupGetInfo`, optional rename through `NetGroupSetInfo`, `NetGroupAddUser`, `NetGroupDelUser`, `NetGroupSetUsers`, `NetUserDel`, and `NetGroupDel`.

Control flow: the test first deletes fixed names `torture_test_group`, `torture_test_group2`, and `torture_test_user`, creates a group, verifies duplicate add fails, enumerates levels 0-3 looking for the group, queries levels 0-3 while tolerating status 124 for not-implemented, attempts rename and tolerates not-supported/not-implemented, creates a user via shared `test_netuseradd`, checks membership absence/presence across operations, and finally deletes user and group.

State and persistence: mutates the target SAM database by creating/deleting global groups and a user, renaming a group when supported, and changing group membership. Test buffers are allocated with `NetApiBufferAllocate` and freed with `NetApiBufferFree`.

Dependencies/integration: depends on user creation helper from `netuser.c`, group structs from `netapi.h`, and shared macros from `common.h`. It requires credentials with account-management rights on the target.

Risks: fixed object names can collide with concurrent test runs or preexisting accounts. Failure paths before cleanup can leave accounts/groups behind, though the start cleanup makes later runs recover. The disabled zero-member `NetGroupSetUsers` block leaves one membership edge untested. Some status handling uses raw numeric codes 50 and 124, which can obscure platform-specific error mapping.

Test signals: run in isolated domains, verify all levels return expected structures, add concurrency isolation with unique names, enable membership wipe tests once supported, and inspect SAM state after failure injection.
