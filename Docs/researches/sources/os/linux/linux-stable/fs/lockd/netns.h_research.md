# File Research: sources/os/linux/linux-stable/fs/lockd/netns.h

Defines lockd per-network-namespace state.

`struct lockd_net` stores:
- Service user count.
- Next host-GC timestamp and host count.
- Configurable grace time and TCP/UDP ports.
- Delayed work for ending grace period.
- `struct lock_manager lockd_manager`.
- Per-net list of NSM handles.

Declares `lockd_net_id` for `net_generic()` lookup.
