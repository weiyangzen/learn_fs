# sources/user-network-fs/samba/source3/smbd/notify_msg.c

## Purpose
This file is the smbd-side messaging adapter for asynchronous file change notify. It finds the local notify daemon, registers to receive `MSG_PVFS_NOTIFY` callbacks, sends interest changes to notifyd, removes registrations, and sends explicit trigger messages when smbd itself changes the filesystem.

## Important APIs, Types, and Functions
`struct notify_context` stores the notify daemon `server_id`, messaging context, `smbd_server_connection`, and smbd callback. `notify_init()` allocates the context, looks up `"notify-daemon"` in `messaging_names_db()`, and optionally registers `notify_handler()`. `notify_add()` sends a `notify_rec_change_msg` with filter, subdir filter, creation time, private data, and path. `notify_remove()` sends the same record shape with only `private_data` and path, relying on zero filters to mean delete. `notify_trigger()` sends `notify_trigger_msg` plus `dir/name` joined by a slash.

## Control Flow
An smbd caller initializes once with `notify_init()`. For a client change-notify request, `notify_add()` builds a two-element iovec containing the fixed header and nul-terminated path, then sends `MSG_SMB_NOTIFY_REC_CHANGE` to notifyd. Cancellation uses `notify_remove()` with the same private token. When notifyd later sends `MSG_PVFS_NOTIFY`, `notify_handler()` validates minimum length and nul termination, casts the payload to `notify_event_msg`, builds a lightweight `notify_event`, and invokes the smbd callback with the original private data and timestamp. Local filesystem changes call `notify_trigger()` to send `MSG_SMB_NOTIFY_TRIGGER` to notifyd.

## State and Persistence
The file stores no persistent database. The only state is the talloc-owned `notify_context` and its messaging registration. The daemon's server id is captured at init time; if notifyd disappears and a new one appears, this context does not perform an automatic lookup refresh.

## Dependencies and Integration Points
It depends on Samba messaging, generated notify/messaging structs, server-id database utilities, and smbd globals/prototypes. It is a direct peer of `notifyd.c`: message formats declared in `notifyd.h` must stay binary-compatible with the iovec layouts here. It also connects to higher SMB request handling through the callback passed to `notify_init()`.

## Risks and Edge Cases
All payload parsing uses direct struct casts after length checks, so ABI layout and alignment must match sender and receiver. `notify_remove()` does not set creation time or filters and assumes zero-initialized `notify_rec_change_msg` remains the delete contract. `notify_trigger()` ignores send status, which avoids slowing hot filesystem paths but can drop notifications silently if notifyd is unavailable. A null context returns `NOT_IMPLEMENTED` for add/remove and no-ops for trigger, so callers must tolerate disabled notify.

## Test Signals
`notifyd/test_notifyd.c` exercises the protocol end to end through `fcn_wait_send()` rather than this exact smbd wrapper. Integration tests should verify `notify_init()` failure when no daemon is registered, correct private-data round trip in `notify_handler()`, add/remove iovec path termination, and trigger path construction from directory plus name.
