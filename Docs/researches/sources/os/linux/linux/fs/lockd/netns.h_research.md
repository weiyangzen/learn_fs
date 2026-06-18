# File Research: sources/os/linux/linux/fs/lockd/netns.h

Purpose: Defines per-network-namespace lockd state.

Key fields:
- `nlmsvc_users` tracks users of the lockd service in a namespace.
- `next_gc`, `nrhosts` support host cache garbage collection/accounting.
- `gracetime`, `tcp_port`, `udp_port` store configurable server settings.
- `grace_period_end` delayed work and `lockd_manager` coordinate grace-period lock management.
- `nsm_handles` holds cached NSM monitor handles.

Dependencies and integration:
- Used by host management, monitor cache, procfs grace endpoint, and netlink/server configuration.
- Exposes `lockd_net_id` for `net_generic()` lookups.

Risk notes:
- Namespace-local state affects host GC, NSM identity cache, and grace management; handlers must use the correct current/request namespace.
