# File Research: sources/os/bsd/freebsd-src/sbin/routed/output.c

RIP packet construction, route-table export, split horizon, route aggregation, authentication emission, broadcasts, and queries.

Key responsibilities:
- Initializes shared RIPv1/RIPv2-compatible and RIPv2-only packet buffers.
- Sends RIP packets as query replies, unicasts, broadcasts, or multicasts with correct sockets and interface selection.
- Chooses outgoing authentication keys and emits cleartext or MD5 RIPv2 authentication records.
- Walks the daemon route table and converts routes into advertisement entries.
- Applies supplier/quiet policy, fake default routes, multihomed host retention, host-route suppression, split horizon, poison reverse, outgoing metric adjustments, and route tags.
- Aggregates or deaggregates routes based on RIPv1/RIPv2 compatibility, subnet/supernet policy, and query mode.
- Sends full or flash broadcasts to all eligible interfaces.
- Sends one-time RIP table requests on eligible interfaces.

Dependencies:
- Uses route radix walking, aggregation helpers (`ag_check`, `ag_flush`), interface state, auth config, MD5, global timers, and socket output from `main.c`.

Notable risks:
- Advertisement semantics differ between RIPv1-compatible and full RIPv2 buffers; fields such as mask/tag/next-hop must be zeroed for old listeners.
- Split-horizon and poison-reverse state mutates per-route poison tracking while generating output.
- Multicast interface selection is global per socket and must track the selected outgoing interface correctly.
