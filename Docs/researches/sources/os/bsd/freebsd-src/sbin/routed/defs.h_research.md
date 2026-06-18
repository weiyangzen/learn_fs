# File Research: sources/os/bsd/freebsd-src/sbin/routed/defs.h

Purpose: central shared definitions for the FreeBSD `routed` RIPv2 routing daemon.

Contents:
- Includes system networking, routing, socket, radix, sysctl, and RIP protocol headers.
- Defines routing constants, timer intervals, packet buffer sizes, router discovery constants, and helper macros.
- Defines `struct rt_entry`, route state flags, route spares/alternate gateways, and route selection macro `BETTER_LINK`.
- Defines `struct interface` with address/mask data, flags, RIP state, authentication keys, statistics, and router discovery state.
- Defines extensive interface state flags for aliases, remote/passive/external interfaces, RIP input/output policy, multicast, router discovery, aggregation, and health.
- Defines aggregation structures `ag_info`, parameter structures `parm`, internal-network/trusted-router lists, output buffers, global state externs, tracing globals, and radix root.
- Declares cross-module functions for sockets, RIP I/O, logging, parameters, tracing, router discovery, route aging/table operations, address masks, interface lookup/health, and authentication.

Integration: included by most `routed` daemon implementation files. It is the daemon’s shared ABI: route table, interface inventory, timers, authentication, tracing, RIP output, and kernel route synchronization all meet here.

Risk notes: very high coupling through global externs and macros. Many bit flags interact, so behavior depends on consistent flag interpretation across modules. The daemon is IPv4/RIP-focused and uses FreeBSD-specific routing and interface APIs.
