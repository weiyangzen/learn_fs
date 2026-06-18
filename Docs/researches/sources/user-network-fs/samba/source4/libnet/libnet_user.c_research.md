# sources/user-network-fs/samba/source4/libnet/libnet_user.c

## Purpose

`libnet_user.c` implements higher-level libnet user management operations: create user, delete user, modify user, fetch user info, and enumerate users. It composes domain-open prerequisites, SAMR RPC helpers, LSA domain queries, and asynchronous composite control flow into public libnet APIs.

## Important APIs, Types, and Functions

Public sync/async pairs include `libnet_CreateUser_send/recv()` plus `libnet_CreateUser()`, `libnet_DeleteUser_send/recv()` plus `libnet_DeleteUser()`, `libnet_ModifyUser_send/recv()` plus `libnet_ModifyUser()`, `libnet_UserInfo_send/recv()` plus `libnet_UserInfo()`, and `libnet_UserList_send/recv()` plus `libnet_UserList()`.

Supporting functions and state:
- `samr_domain_opened()` and `lsa_domain_opened()` from `prereq_domain.c` gate cached domain-handle use.
- `libnet_rpc_useradd`, `libnet_rpc_userdel`, `libnet_rpc_userinfo`, and `libnet_rpc_usermod` are lower-level SAMR helpers.
- `set_user_changes()` compares current `samr_UserInfo21` values with requested `libnet_ModifyUser` fields and sets `usermod_change` fields/flags using macros from `libnet_user.h`.

## Control Flow

Create/delete operations ensure a SAMR domain handle is open, then call the low-level add/delete RPC helper. Modify opens SAMR, queries level-21 user info, computes only changed fields, and sends a usermod request. UserInfo opens SAMR, either resolves name with `libnet_LookupName()` then queries by SID/RID or queries directly by SID, and maps level-21 SAMR output into friendly fields and `timeval`s. UserList opens LSA first to query the domain SID, opens SAMR, calls `samr_EnumDomainUsers`, and builds username/SID strings from returned RIDs.

## State and Persistence Behavior

Create, delete, and modify mutate remote SAM database state. UserInfo and UserList are read-only. The file relies on `libnet_context` cached SAMR/LSA domain handles and names, so state can persist across calls in one context. Results are talloc-stolen into caller memory contexts. UserList supports SAMR resume handles and treats `STATUS_MORE_ENTRIES` and `NT_STATUS_NO_MORE_ENTRIES` as successful enumeration statuses.

## Dependencies and Integration Points

Dependencies include composite/tevent, SAMR and LSA generated stubs, libnet domain-open and lookup helpers, lower-level user add/delete/info/modify modules, security/SID utilities, and credentials. Python `Net.create_user()` and `Net.delete_user()` expose part of this file. Torture tests in `source4/torture/libnet/libnet_user.c`, `userinfo.c`, `groupinfo.c`, and `userman.c` exercise related paths.

## Risks and Edge Cases

Several optional monitor paths allocate or send uninitialized `monitor_msg msg` values in create/delete/modify domain-open continuations. `continue_rpc_userinfo()` computes status from `set_user_changes()` but does not check it before sending usermod. `ModifyUser_recv()` does not populate output error strings. `SET_FIELD_ACCT_FLAGS` cannot set account flags to zero because it treats zero as not requested. UserList allocates based on returned SAM array count and assumes `sam` is non-NULL when status allows. Cached-domain logic can reject NULL domain inputs if a handle is already open.

## Test Signals

Torture user-management tests are the key signal. Good coverage includes create/delete idempotence, modify no-op and changed-field behavior, name-vs-SID user info, exact SID construction, time conversion, account flag edge cases, paged enumeration with resume handles, monitor callbacks, and error strings on lookup/open/query failures.
