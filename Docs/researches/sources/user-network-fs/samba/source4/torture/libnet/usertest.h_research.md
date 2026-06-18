# sources/user-network-fs/samba/source4/torture/libnet/usertest.h

## Purpose
This header centralizes test usernames, user-modification field enumeration, duplicate-field skipping logic, and string templates shared by libnet user tests.

## Important APIs, types, and functions
It defines `TEST_USERNAME`, `continue_if_field_set(field)`, `USER_FIELD_FIRST`, `USER_FIELD_LAST`, enum `test_fields`, and templates such as `TEST_CHG_ACCOUNTNAME`, `TEST_CHG_DESCRIPTION`, `TEST_CHG_FULLNAME`, `TEST_CHG_COMMENT`, and `TEST_CHG_PROFILEPATH`.

## Control flow
The header has no standalone control flow. `libnet_user.c` and `userman.c` iterate from `USER_FIELD_FIRST` to `USER_FIELD_LAST` and use enum values to choose which account property to modify.

## State and persistence behavior
No state is stored in the header, but its fixed username and generated account-name templates determine persistent domain objects created by the tests.

## Dependencies and integration points
The enum names must match fields and bit flags used by `libnet_ModifyUser` and `libnet_rpc_usermod` test code. The macro assumes the caller is inside a loop with an `i` loop variable.

## Risks and edge cases
The `continue_if_field_set` macro mutates `i`, so it is tightly coupled to callers and can be surprising if reused elsewhere. Fixed names increase collision risk after failed test cleanup.

## Test signals
The header indirectly drives coverage for all user modification fields in the high-level and lower-level libnet user tests.
