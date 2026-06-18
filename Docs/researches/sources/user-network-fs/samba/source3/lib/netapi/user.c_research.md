# sources/user-network-fs/samba/source3/lib/netapi/user.c

## Purpose
This file implements source3 libnetapi user-management calls on top of remote SAMR RPC. It covers `NetUserAdd`, `NetUserDel`, `NetUserEnum`, `NetQueryDisplayInformation`, `NetUserGetInfo`, `NetUserSetInfo`, `NetUserModalsGet`, `NetUserModalsSet`, `NetUserGetGroups`, `NetUserSetGroups`, and `NetUserGetLocalGroups`; local entry points redirect to localhost through `LIBNETAPI_REDIRECT_TO_LOCALHOST`.

## Important APIs, Types, And Functions
The central internal type is `USER_INFO_X`, a normalized view of many NetAPI `USER_INFO_*` input levels. `construct_USER_INFO_X()` reads caller buffers for levels 0, 1, 2, 3, 1003, 1006, 1007, 1009, 1011, 1012, 1014, 1024, 1051, 1052, and 1053. `convert_USER_INFO_X_to_samr_user_info21()` marks SAMR fields present and builds `samr_UserInfo21`; `set_user_info_USER_INFO_X()` sends it via SAMR info level 21, 23, or 25 depending on whether a password is supplied and whether `SetUserInfo2` supports encrypted password level 25.

Read paths use `libnetapi_samr_lookup_user()` and `libnetapi_samr_lookup_user_map_USER_INFO()` to open users, query level 21, query DACLs, derive builtin alias membership auth flags, and map to NetAPI levels 0, 1, 2, 3, 4, 10, 11, 20, and 23. Domain policy helpers map SAMR domain info classes 1, 3, 5, 6, 7, and 12 to `USER_MODALS_INFO_*` structures. Group helpers create `GROUP_USERS_INFO_0/1` and `LOCALGROUP_USERS_INFO_0` arrays.

## Control Flow
Every remote public function opens a SAMR pipe, opens the account domain and sometimes the builtin domain, validates level-specific access masks, performs lookup/open/query/set calls, maps `NTSTATUS` to `WERROR`, and conditionally closes cached handles when `ctx->disable_policy_handle_cache` is set. `NetUserAdd_r()` creates a user with `samr_CreateUser2`, validates the account flags, obtains the transport session key for password encryption, sets attributes, and deletes the created user on post-create failure. `NetUserDel_r()` removes the SID from the foreign builtin domain before deleting the user. Enumeration first calls `samr_EnumDomainUsers`, then expands every returned RID through the same per-user mapper. Group setting computes add and delete RID lists by diffing requested group membership against `samr_GetGroupsForUser`.

## State And Persistence
The file itself stores no durable state. Persistent effects are SAMR account database changes: users, passwords, attributes, domain password/lockout policy, and group membership. It also depends on libnetapi policy-handle caches and talloc ownership for output buffers. Password setting depends on the RPC transport session key and encrypted SAMR password blobs.

## Dependencies And Integration Points
It integrates `librpc/gen_ndr/libnetapi.h`, source3 libnetapi private helpers, generated SAMR client stubs, LSA string initialization, DS account flag mappings, SID utilities, security descriptors, and RPC pipe/session-key helpers. Builtin alias checks use well-known alias RIDs to emulate NetAPI auth flags such as print/server/account operators.

## Risks And Test Signals
Risk concentrates around incomplete level support, level-to-access-mask mismatches, stale policy-handle cache behavior, password encryption fallback, time conversions, memory ownership of ADD_TO_ARRAY outputs, and correctness of builtin/domain SID membership mapping. `NetUserGetLocalGroups_r()` collects aliases from both domain and builtin handles but then resolves all RIDs through the builtin handle, which is worth regression coverage for domain-local aliases. Tests should exercise supported and rejected info levels, add rollback, delete with builtin membership, pagination/resume status from enumeration, modals get/set levels 0/3/1001-1005, password set level 1003, group diff add/delete idempotence, and SAMR partial status such as `STATUS_SOME_UNMAPPED`.
