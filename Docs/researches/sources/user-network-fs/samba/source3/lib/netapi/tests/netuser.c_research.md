# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netuser.c

Purpose: destructive integration tests for user account NetAPI operations and user modals policy calls. It creates a user, enumerates/query levels, changes a comment, verifies group listing, deletes the user, and round-trips modals level 0.

Important APIs/functions: `test_netuserenum` covers `NetUserEnum` levels 0, 1, 2, 3, 4, 10, 11, 20, and 23. `test_netuseradd` creates a level 1 user with a fixed password and comment. `test_netusermodals` calls `NetUserModalsGet` levels 0-3, writes level 0 back through `NetUserModalsSet`, and compares the result. `test_netusergetgroups` enumerates a user's global groups at levels 0 and 1. `netapitest_user` orchestrates add, enum, get-info, set-info level 1007, delete, and modals tests.

Control flow: fixed users `torture_test_user` and `torture_test_user2` are deleted first. A user is created, enumerated across supported levels, queried across the same levels with status 124 tolerated, group membership is enumerated, the comment is changed with `USER_INFO_1007`, queries are repeated, the user is deleted, deletion is verified by expecting get-info failure, and modals are tested. Cleanup deletes both fixed users again on exit.

State and persistence: mutates the target SAM by creating/deleting users, changing a user comment, and writing user modals policy level 0 back to its existing value. The fixed password is embedded in source. Buffers are freed in enumeration helpers but not consistently after get-info/modals calls.

Dependencies/integration: depends on public user, group-users, and modals structs, shared status helpers, and administrative credentials. Other test modules call `test_netuseradd`.

Risks: fixed names/passwords and policy writes require isolated test targets. Writing modals level 0 back should be idempotent but still exercises a persistent policy path and could alter state if structures include server-normalized fields. `memcmp` on `USER_MODALS_INFO_0` assumes no padding differences; the struct currently contains only `uint32_t` fields, making that acceptable. Leak detectors may flag unfreed get-info/modals buffers.

Test signals: use unique account names, assert actual field values after set-info, verify password policy remains unchanged, add negative tests for duplicate user add/delete missing user, and run under leak/sanitizer tooling.
