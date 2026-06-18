# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/netstack.h

## Purpose

`netstack.h` defines the illumos per-network-stack framework used by IP-adjacent kernel modules to maintain separate module state per shared or exclusive-IP zone. It is a public kernel coordination header for netstack identifiers, module registration, per-module lifecycle callbacks, kstat scoping, reference management, and stack iteration.

## Main Interfaces

The file defines `netstackid_t`, `GLOBAL_NETSTACKID`, and the ordered `NS_*` module slots from `NS_DLS` through `NS_ILB`. The ordering is explicitly meaningful: create callbacks run in ascending order and destruction runs in descending order.

Under `_KERNEL`, `nm_state_t` tracks per-module callback state with a flags word and condition variable. User-level consumers get a dummy `uint_t` type for build compatibility. The `NSS_*` flags distinguish needed, in-progress, and completed create/shutdown/destroy transitions.

`struct netstack` contains a typed union over module private pointers, a parallel `netstack_modules[NS_MAX]` array, per-module state, locks, linked-list pointer, stack id, zone usage count, hold/release reference count, lifecycle flags, and a kernel condition variable. Macros such as `netstack_ip`, `netstack_tcp`, and `netstack_ilb` provide typed field names for each slot.

`struct netstack_registry` stores callback function pointers for a module: create, shutdown, and destroy, plus registration flags.

Exported operations include initialization, hold/release, active holds, lookup by credentials/stack id/zone id, zone/stack id conversion, current-stack lookup, module registration/unregistration, netstack-scoped kstat create/delete, and iterator-style walking via `netstack_next_init()`, `netstack_next()`, and `netstack_next_fini()`.

## Runtime Use

This header does not implement control flow, but it defines the synchronization and lifecycle contract used by `netstack.c` and networking modules. Consumers register a module slot and callbacks, then store per-stack private state in the corresponding typed pointer inside `netstack_t`.

A caller that walks all netstacks must release every `netstack_t *` returned by `netstack_next()`. Most fields are protected by `netstack_lock`; `netstack_next` is protected by the global netstack lock.

## Dependencies

Includes `sys/kstat.h`, `sys/cred.h`, and `sys/mutex.h`. The typed module pointers are forward references to networking subsystem private stack structures such as `ip_stack`, `tcp_stack`, `udp_stack`, `sctp_stack`, `dls_stack`, and IPsec-related stack types.

## Risks and Invariants

The `NS_*` order is a hard lifecycle invariant. Adding or reordering slots can break dependency-sensitive create and destroy sequencing.

The union and accessor macros require `NS_MAX` and the typed field list to remain synchronized. A mismatch would corrupt module-private state indexing.

Reference ownership is explicit: lookups and iteration can return held stacks, and missing `netstack_rele()` calls leak references or block teardown.
