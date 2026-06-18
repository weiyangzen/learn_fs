# sources/user-network-fs/samba/source3/smbd/notifyd/notifyd.h

## Purpose
This header defines notifyd's public protocol and startup interface. It documents the smbd-to-notifyd architecture, the message payloads exchanged over Samba messaging, and the system watch callback signature used to plug in inotify or another backend.

## Important APIs, Types, and Functions
`struct notify_instance` is the per-client interest record: creation time, direct filter, subdir filter, and private data token. `struct notify_rec_change_msg`, `struct notify_trigger_msg`, and `struct notify_event_msg` are variable-length message payloads for interest changes, triggers, and delivered events. `sys_notify_watch_fn` is the backend callback type. `notifyd_send()` starts the daemon as a tevent request; `notifyd_recv()` receives its terminal status.

## Control Flow
The comments describe smbd processes sending interest and trigger messages to a local notifyd, while notifyd multicasts events to interested clients. In clustered deployments, notifyd peers exchange enough information to avoid every smbd talking to every other smbd directly.

## State and Persistence
The header declares protocol structs but owns no storage. The flexible array `path[]` members make all message formats dependent on iovec assembly and explicit nul termination by senders. `private_data` is intentionally opaque and is returned to the original client.

## Dependencies and Integration Points
It includes generated notify and messaging definitions, dbwrap and tdb headers, Samba messages, and utility headers. It is included by smbd wrappers, notifyd implementation, notifyd db walking code, test helpers, and the notify daemon launcher.

## Risks and Edge Cases
Because protocol payloads contain native `struct timespec` and `void *`, the messages are local-process or same-architecture Samba messaging contracts, not portable wire formats. Any change to these structs must be coordinated across all senders and receivers. The comments mention a proxied flag for loop prevention, while the current implementation uses source vnn/server-id logic and peer databases, so documentation and implementation should be checked together when changing cluster behavior.

## Test Signals
Build coverage comes from the `notifyd`, `fcn_wait`, `notifyd_db`, and torture modules. Behavior is validated indirectly by tests that send and receive these message structs.
