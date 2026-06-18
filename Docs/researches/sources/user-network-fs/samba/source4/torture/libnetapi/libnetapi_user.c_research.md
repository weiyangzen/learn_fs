# sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi_user.c

## Purpose
`libnetapi_user.c` tests source3 NetAPI user management from smbtorture, including add/delete, enumeration, info query/set, group membership lookup, and user modals.

## Important APIs, types, and functions
`test_netuserenum()` enumerates users for levels 0, 1, 2, 3, 4, 10, 11, 20, and 23. `test_netuseradd()` creates a normal user with `USER_INFO_1`. `test_netusermodals()` gets levels 0-3, writes level 0 back, and verifies the struct is unchanged. `test_netusergetgroups()` validates group-list returns for levels 0 and 1. `torture_libnetapi_user()` drives the full lifecycle.

## Control flow
The main test deletes stale users, adds `torture_testuser`, confirms enumeration at all supported levels, queries info levels, checks group lookup, modifies the comment using `USER_INFO_1007`, queries again, renames using `USER_INFO_0`, deletes the renamed account, verifies it is gone, then tests user modals.

## State and persistence behavior
It creates, renames, modifies, and deletes `torture_testuser` and `torture_testuser2`. The modal test reads and writes domain user policy level 0 back to the server, which should be idempotent but is still a persistent write path.

## Dependencies and integration points
The file uses public NetAPI calls from `<netapi.h>`, libnetapi context/error helpers, and exposes `test_netuseradd()` for group tests. It depends on account-management privileges and host configuration.

## Risks and edge cases
Info levels returning status 124 are treated as acceptable unimplemented cases. The fixed password must satisfy server policy. User rename and modal set operations require more privilege than read-only enumeration.

## Test signals
Passing tests show NetUser lifecycle operations, enumeration levels, comment mutation, rename/delete semantics, group lookup, and modal get/set round trips function through libnetapi.
