# sources/user-network-fs/samba/source3/utils/net_notify.c

## Purpose
This file implements `net notify`, a local client for Samba notifyd messaging. It can register for change notifications on a path or send synthetic trigger events.

## Important APIs, Types, And Control Flow
`net_notify()` validates that a messaging context exists and dispatches `listen` and `trigger`. `net_notify_listen()` looks up the `notify-daemon` server ID in the messaging names database, registers `net_notify_got_event()` for `MSG_PVFS_NOTIFY`, sends a `MSG_SMB_NOTIFY_REC_CHANGE` request containing filter, subdir filter, and path iovecs, then loops in `tevent_loop_once()`. `net_notify_trigger()` sends a `MSG_SMB_NOTIFY_TRIGGER` message containing action, filter, and path. `net_notify_got_event()` validates minimum blob length and NUL termination before printing action and path.

## State And Persistence
No persistent files are written. Runtime state is entirely in Samba messaging, server-id lookup, and the event loop. `listen` is intentionally long-running until event-loop failure or process termination.

## Dependencies And Integration Points
It depends on Samba messaging, tevent, server ID database APIs, notifyd message structures, and `struct net_context`. It integrates with a running notify daemon and requires privileges/context sufficient to access messaging.

## Risks And Test Signals
Filters and action values are parsed with `atoi()` without validation. `listen` has an infinite loop and no local timeout or signal-aware shutdown path. Message layout safety depends on `offsetof(..., path)` matching notifyd structures. Test no-message-context handling, missing notify daemon, malformed notification blobs, successful listen registration, trigger delivery, and invalid numeric argument behavior.
