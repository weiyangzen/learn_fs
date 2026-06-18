# File Research: sources/os/bsd/freebsd-src/sbin/routed/table.c

## Summary
Core routing-table implementation for FreeBSD `routed`. It maintains the daemon’s radix-tree route table, aggregates routes for advertisements/kernel installation, mirrors kernel routing-table state, reacts to routing-socket messages, and ages stale routes/interfaces.

## Main Responsibilities
- Initializes and manages the IPv4 radix tree used by the daemon route table.
- Aggregates compatible routes with `ag_check()` and flushes pending aggregation slots with `ag_flush()`.
- Installs, changes, or deletes kernel routes through routing-socket `RTM_*` messages.
- Keeps a hash-table shadow of kernel routes to avoid unnecessary kernel updates and to detect externally changed routes.
- Imports kernel routing-table state with `sysctl(CTL_NET, PF_ROUTE, NET_RT_DUMP)`.
- Processes routing socket events in `read_rt()`, including route add/change/delete, redirects, packet-loss notices, and interface-address changes.
- Ages RIP routes, remote interfaces, route spares, redirected routes, and poisoned routes.
- Handles route add/change/delete/switch logic for primary and spare route slots.

## Key Elements
- `ag_slots`, `ag_avail`, `ag_corsest`, `ag_finest`: fixed aggregation workspace ordered by mask coarseness.
- `ag_check()`: promotes even/odd route pairs, suppresses redundant finer routes, preserves sequence/tag/next-hop metadata, and punts non-contiguous masks.
- `rtioctl()` / `kern_ioctl()`: build and send routing messages with destination, gateway, mask, metric, and flags.
- `kern_find()` / `kern_add()`: manage the kernel-route mirror hash.
- `flush_kern()` / `fix_kern()`: synchronize the kernel’s routing table with the daemon’s current table.
- `rtm_add()` / `rtm_lose()` / `del_redirects()`: handle kernel-originated route changes and redirects.
- `rtadd()`, `rtchange()`, `rtswitch()`, `rtdelete()`: core daemon-table mutation paths.
- `walk_age()` / `age()`: periodic aging pass for routes, remote interfaces, and kernel synchronization.

## Dependencies And Integration
Depends on `defs.h` for route/interface structures, macros, timers, tracing hooks, RIP/router-discovery state, and global sockets. Uses BSD radix tree APIs, routing sockets, PF_ROUTE sysctl dumps, interface lookup helpers, and RIP/router-discovery callbacks.

## Research Notes
The file’s central invariant is that the daemon table and kernel table are related but not identical: static kernel routes are preserved and imported into the daemon, redirect-created routes are tracked separately, and daemon route aggregation decides what should actually be installed in the kernel.
