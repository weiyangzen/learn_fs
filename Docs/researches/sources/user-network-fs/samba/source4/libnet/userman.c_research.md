# sources/user-network-fs/samba/source4/libnet/userman.c

## Purpose

`userman.c` implements composite asynchronous helpers for SAMR-backed user management in source4 libnet: create user, delete user, and modify user. It wraps generated SAMR client calls behind `libnet_rpc_useradd_*`, `libnet_rpc_userdel_*`, and `libnet_rpc_usermod_*` APIs, using Samba's `composite_context` and `tevent_req` callback style so callers can drive the operations either asynchronously or synchronously.

## Important APIs, Types, And Functions

The file defines three private state machines. `struct useradd_state` stores the binding handle, domain handle, `samr_CreateUser` request, output user handle, created RID, and optional monitor callback. `struct userdel_state` stores the SAMR lookup, open, and delete requests plus the handles required to delete a resolved account. `struct usermod_state` stores the lookup/open/query/set requests and a mutable copy of `struct usermod_change`.

Public entry points are `libnet_rpc_useradd_send/recv`, `libnet_rpc_useradd`, `libnet_rpc_userdel_send/recv`, `libnet_rpc_userdel`, `libnet_rpc_usermod_send/recv`, and `libnet_rpc_usermod`. The async send functions allocate a composite context, populate SAMR request structs, submit generated `dcerpc_samr_*_r_send()` calls, and install continuation callbacks. The sync functions are thin wrappers around send/recv.

The user modification core is `usermod_setfields()` and `usermod_change()`. `usermod_setfields()` maps bitmask flags from `userman.h` to SAMR user-info levels such as 7 for account name, 8 for full name, 13 for description, 2 for comment, 10 for home path/drive, 11 for logon script, 12 for profile path, 16 for account flags, and 17 for account expiry. `usermod_change()` decides whether a level can be set directly or must first be queried to preserve unrelated fields.

## Control Flow

User creation is a one-stage state machine. `libnet_rpc_useradd_send()` builds `samr_CreateUser`, sends it, and `continue_useradd_create()` receives transport status, checks `createuser.out.result`, copies the returned policy handle and RID, optionally emits `mon_SamrCreateUser`, then completes the composite context.

User deletion is a three-stage state machine. `libnet_rpc_userdel_send()` sends `samr_LookupNames` for one user name. `continue_userdel_name_found()` validates that returned RID/type counts match the requested count, emits `mon_SamrLookupName`, and sends `samr_OpenUser` with `SEC_FLAG_MAXIMUM_ALLOWED`. `continue_userdel_user_opened()` checks open status, emits `mon_SamrOpenUser`, and sends `samr_DeleteUser`. `continue_userdel_deleted()` checks the delete result, emits `mon_SamrDeleteUser`, and completes.

User modification follows lookup, open, and repeated query/set cycles. `continue_usermod_name_found()` resolves the name and opens the user. `continue_usermod_user_opened()` calls `usermod_change()`. If `usermod_setfields()` returns false for a partially populated level, `usermod_change()` sends `samr_QueryUserInfo`; `continue_usermod_user_queried()` copies the returned union, applies the pending field, and sends `samr_SetUserInfo`. `continue_usermod_user_changed()` clears completed flags, completes when no fields remain, or loops back into `usermod_change()`.

## State And Persistence Behavior

All state is transient and talloc-owned by the composite context. The file does not persist to local storage; persistent changes happen remotely through SAMR on the target account database. Output handles are copied back to caller-owned `io` structs in the recv functions. Monitor callback payloads point to stack-local or state-owned data for the duration of the callback only, so consumers must not retain those pointers.

## Dependencies And Integration Points

The implementation depends on `libcli/composite/composite.h`, `libnet/libnet.h`, generated SAMR RPC stubs from `librpc/gen_ndr/ndr_samr_c.h`, LSA strings, SAMR policy handles, and the monitor message types used elsewhere in libnet. It is compiled into the private `samba-net` library by `source4/libnet/wscript_build`.

## Risks

The send functions have uneven argument validation: useradd rejects null binding or io, while userdel/usermod assume valid `b`, `io`, `username`, and allocation success for some input structures. `usermod_setfields()` mutates `change.fields` with XOR, which works only if bits are known and set once; duplicated or unsupported fields can lead to `NT_STATUS_INVALID_PARAMETER`. Some `struct usermod_change` fields declared in the header are not implemented in `usermod_setfields()` even though constants exist or fields are present. Deletion and modification ask for maximum allowed access, increasing dependency on server ACL behavior. Query-before-set is essential for compound SAMR levels; missing coverage there can reset unrelated account attributes.

## Test Signals

Useful tests are SAMR integration tests that create a temporary domain user, modify each supported field individually and in combinations that share a SAMR info level, then delete the user. Negative tests should cover nonexistent users, lookup count mismatches from mocked RPC replies, denied open/delete/set permissions, invalid field masks, and transport failures from generated SAMR client calls. Monitor callback ordering can be validated for create, lookup/open/delete, and lookup/open/query/set flows.
