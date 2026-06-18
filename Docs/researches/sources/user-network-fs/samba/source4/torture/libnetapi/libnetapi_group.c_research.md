# sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi_group.c

## Purpose
`libnetapi_group.c` tests source3 NetAPI group management from smbtorture: add/delete, enumeration, info query/set, membership add/delete/set, and buffer alignment.

## Important APIs, types, and functions
Alignment helpers check `GROUP_INFO_0..3` and `GROUP_USERS_INFO_0..1`. `test_netgroupenum()`, `test_netgroupgetusers()`, and `test_netgroupsetusers()` wrap paged enumeration and membership APIs. `torture_libnetapi_group()` orchestrates `NetGroupAdd`, `NetGroupEnum`, `NetGroupGetInfo`, `NetGroupSetInfo`, `NetGroupAddUser`, `NetGroupDelUser`, `NetGroupSetUsers`, `NetUserDel`, and `NetGroupDel`.

## Control flow
The test deletes stale user/group names, creates a group, verifies a second add fails, enumerates the new group across levels 0-3, queries info levels, optionally renames the group via level 0 set-info, creates a user using `test_netuseradd()`, checks non-membership, adds and removes membership, sets membership explicitly, deletes the user and group, then verifies the group no longer exists.

## State and persistence behavior
It persistently creates and deletes `torture_test_group`, optional `torture_test_group2`, and `torture_test_user`. Cleanup occurs at the beginning and during normal success flow; failures can leave objects behind until a later run's initial cleanup.

## Dependencies and integration points
The file uses public `<netapi.h>` calls, libnetapi error formatting, the shared `torture_libnetapi_init_context()`, `test_netuseradd()` from `libnetapi_user.c`, and alignment helpers from `lib/util/alignment.h`.

## Risks and edge cases
Some NetAPI calls are accepted as unsupported/not implemented for specific levels, so status handling must distinguish expected gaps from failures. Membership checks are case-insensitive. Alignment checks guard ABI correctness of returned buffers.

## Test signals
Passing tests show group lifecycle and membership APIs work across several info levels, returned buffers are correctly aligned, resume handles enumerate all results, and deleted groups become unqueryable.
