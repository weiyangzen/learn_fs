# sources/user-network-fs/samba/source4/torture/libnet/libnet_user.c

## Purpose
This file tests high-level libnet user account APIs for create, delete, modify, info, and paged listing against a live domain.

## Important APIs, types, and functions
Entry points are `torture_createuser()`, `torture_deleteuser()`, `torture_modifyuser()`, `torture_userinfo_api()`, and `torture_userlist()`. `set_test_changes()` builds randomized `libnet_ModifyUser` changes for account name, full name, description, home directory/drive, comment, logon script, profile path, expiry, and account flags. Verification uses `libnet_UserInfo` and macros for string, time, and numeric fields.

## Control flow
Create and delete tests combine low-level helper setup with high-level libnet calls. The modify test creates `libnetusertest`, then walks every field in `usertest.h`, applying one change at a time and reading the user back to compare. `torture_userinfo_api()` creates a user and queries it by name through `libnet_UserInfo`. The user-list test pages through `libnet_UserList` with resume indexes and closes both SAMR and LSA handles.

## State and persistence behavior
The tests create, rename, modify, and delete domain users. Because account-name changes can rename the test user, cleanup must use the original RDN-aware helper that can query LDAP for `sAMAccountName`. Failed modification or cleanup can leave test users with randomized attributes in the directory.

## Dependencies and integration points
This file relies on `utils.c` helper functions, `usertest.h` field definitions and test string patterns, SAMR/LSA generated RPC clients, command-line credentials, and loadparm workgroup settings. It validates high-level libnet APIs against direct SAMR-created setup state.

## Risks and edge cases
Randomized field values and account renames make cleanup fragile. Time comparison requires exact round-trip conversion. Account flags must match server-side normalization. Required privileges are high because the tests create, modify, delete, and enumerate users.

## Test signals
The strongest signal is the per-field modify loop: each libnet user modification is immediately checked through `libnet_UserInfo`. Listing also verifies resume-driven account enumeration and handle close behavior.
