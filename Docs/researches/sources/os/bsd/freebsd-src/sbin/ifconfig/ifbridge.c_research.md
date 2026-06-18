# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifbridge.c

`ifbridge.c` implements bridge interface status and configuration commands. It uses `SIOCSDRVSPEC`/`SIOCGDRVSPEC` driver-specific ioctls through `do_cmd()` for mutations and `libifconfig` for full bridge status.

Status prints bridge ID, priority, timers, STP protocol/root details, cache sizing, bridge flags, default untagged VLAN, member ports, member flags, STP role/state/protocol, VLAN protocol, untagged VLAN, and tagged VLAN ranges. It can also dump the forwarding cache with MAC, VLAN, interface, expiry, and flags.

Commands cover adding/removing members, span ports, member flags, STP settings, edge/ptp options, flushing dynamic/all cache entries, static cache entries and deletions, max address counts, bridge timers, priorities, path costs, VLAN filter/default VLAN/QinQ behavior, member tagged/untagged VLAN sets, and VLAN protocol. VLAN set parsing supports `none`, `all`, comma-separated values, and ranges while excluding reserved VLAN IDs for `all`.
