# sources/user-network-fs/samba/source4/libnet/userinfo.c

## Purpose

`userinfo.c` implements a lower-level composite SAMR helper for querying user information by username or SID/RID using an already-open SAMR domain handle and binding handle.

## Important APIs, Types, and Functions

Public functions are `libnet_rpc_userinfo_send()`, `libnet_rpc_userinfo_recv()`, and synchronous `libnet_rpc_userinfo()`.

Internal continuation stages:
- `continue_userinfo_lookup()` receives `samr_LookupNames`, validates one RID/type, emits lookup monitor data, and sends `samr_OpenUser`.
- `continue_userinfo_openuser()` receives `samr_OpenUser`, emits open monitor data, and sends `samr_QueryUserInfo` at the requested level.
- `continue_userinfo_getuser()` receives `samr_QueryUserInfo`, steals the returned union, emits query monitor data, and sends `samr_Close`.
- `continue_userinfo_closeuser()` receives `samr_Close`, emits close monitor data, and completes the composite request.

## Control Flow

`send()` creates a composite context and state. If `io->in.sid` is present, it parses the SID string and extracts the last subauthority as the RID, skipping name lookup. Otherwise it sends `samr_LookupNames` for `io->in.username`. Both paths converge on open-user, query-user-info, close-user. `recv()` waits, steals the resulting `union samr_UserInfo` into the caller context, frees the composite context, and returns status.

## State and Persistence Behavior

The helper is read-only except for opening and closing a remote SAMR user policy handle. It depends on caller-provided domain and binding handles but does not cache them. Result data is talloc-transferred to the caller.

## Dependencies and Integration Points

Dependencies include composite/tevent, generated SAMR client stubs, SID parsing, security constants, and libnet monitor message types. `libnet_user.c` uses it for high-level `UserInfo` and `ModifyUser`, and torture tests call it directly in sync and async modes.

## Risks and Edge Cases

SID parsing uses the last subauthority as RID without verifying that the SID belongs to the opened domain. If `io->in.sid` and `io->in.username` are both absent, the username path can dereference NULL through `talloc_strdup`. Monitor payloads allocate under state but no allocation failures are checked before invoking callbacks. If close fails after query success, the whole operation fails even though info was fetched.

## Test Signals

`source4/torture/libnet/userinfo.c`, `groupinfo.c`, and `userman.c` provide direct signals. Tests should cover SID and username paths, bad SID strings, non-user RIDs, missing username, query levels, monitor messages, close failure behavior, and memory ownership of returned info.
