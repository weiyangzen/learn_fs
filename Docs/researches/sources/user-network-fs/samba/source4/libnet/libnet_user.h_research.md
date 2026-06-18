# sources/user-network-fs/samba/source4/libnet/libnet_user.h

## Purpose

`libnet_user.h` declares public libnet user-management request/response structures and helper macros for comparing requested user modifications to current SAMR level-21 state.

## Important APIs, Types, and Functions

Structures include `libnet_CreateUser`, `libnet_DeleteUser`, `libnet_ModifyUser`, `libnet_UserInfo`, and `libnet_UserList`. `enum libnet_UserInfo_level` selects lookup by name or SID.

Macros:
- `SET_FIELD_LSA_STRING()` copies a changed string and sets a `USERMOD_FIELD_*` flag.
- `SET_FIELD_NTTIME()` converts a requested `timeval` to NTTIME and flags changed time fields.
- `SET_FIELD_UINT32()` compares scalar fields.
- `SET_FIELD_ACCT_FLAGS()` flags nonzero account flags only when changed.

## Control Flow

The macros are invoked by `set_user_changes()` in `libnet_user.c` after the current user info is fetched. The structs drive async and sync public APIs.

## State and Persistence Behavior

The header models remote user/account state. Create/delete/modify requests mutate SAMR state; info/list outputs return allocated field values, SIDs, times, and arrays.

## Dependencies and Integration Points

It relies on `struct timeval`, `struct dom_sid`, and lower-level usermod field flags from libnet headers. Python bindings and C torture tests construct these structures.

## Risks and Edge Cases

The account-flags macro cannot request zero. Time macros treat NULL as not requested. String macros distinguish NULL from empty string, so callers can set empty strings only if they pass a non-NULL empty value.

## Test Signals

Tests should cover all modify field flags, especially clearing fields, zero account flags, and time conversion boundaries. Compile-time coverage protects structure layout expected by callers.
