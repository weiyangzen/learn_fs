# sources/user-network-fs/samba/source3/smbd/notifyd/fcn_wait.h

## Purpose
This header exposes the asynchronous file-change-notify wait helper used by notifyd tests and utilities. It declares the send/receive pair implemented in `fcn_wait.c`.

## Important APIs, Types, and Functions
`fcn_wait_send()` accepts a talloc context, tevent context, messaging context, notifyd server id, path, direct filter, and recursive subdir filter, then returns a `struct tevent_req *`. `fcn_wait_recv()` receives one queued event from that request and can return the event timestamp, action, and talloc-duplicated relative path.

## Control Flow
Callers start a request with `fcn_wait_send()`, poll or wait for tevent completion notifications, then call `fcn_wait_recv()`. The receive side may return `NT_STATUS_RETRY` if the request is still alive but no queued event is available, `NT_STATUS_CANCELLED` after explicit cancellation, or `NT_STATUS_OK` with one event.

## State and Persistence
The header itself owns no state. Its API implies that request lifetime controls registration lifetime and queued event storage. The returned path is allocated under the caller-supplied memory context in `fcn_wait_recv()`.

## Dependencies and Integration Points
It includes Samba replacement types, messaging declarations, and generated `server_id`. It intentionally hides `notifyd.h` internals from callers except through filter values and notifyd server id.

## Risks and Edge Cases
The API does not document ownership in comments, so callers must infer talloc lifetimes from Samba tevent conventions. Since the helper registers live interest in notifyd, callers should cancel or free the request to avoid stale notifyd entries.

## Test Signals
The header is compiled through the `fcn_wait` subsystem in `wscript_build` and used by `test_notifyd.c`. API-level compatibility is validated when the torture module builds and links.
