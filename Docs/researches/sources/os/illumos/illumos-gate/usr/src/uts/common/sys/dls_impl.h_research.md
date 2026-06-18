# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dls_impl.h

## Scope

Complete file read, 137 lines. This is the private DLS implementation header for link, multicast, and stream-head state.

## Public Surface

It defines:

- `dls_multicst_addr_t`: linked multicast address entry.
- `struct dls_link_s`: link name, DDI instance, MAC handles, notification handle, MAC info, reference counts, stream hash, active counts, unknown packet count, zone ownership/reference, tag mode, and non-IP count.
- `dls_head_t`: stream list head with lock, reference, hash key, condition variable, and removal flag.
- Global `i_dls_link_hash`.
- Internal link lifecycle, hold/release, add/remove, zone, devinfo/dev, active-state, kstat, devnet link hold/open/release, initialization/finalization, transmit loop, receive filtering, promiscuous receive, active set/clear, management init/fini, and physical-dev lookup prototypes.

## Behavior And Integration

DLS implementation files use these structures to map devnet links to MAC clients, maintain per-link stream membership, perform receive acceptance for normal/promiscuous/loopback paths, and expose link kstats.

## Dependencies And Invariants

The locking annotations in field comments are part of the contract: serializer, modhash lock, atomic, and zone/ref rules must be respected. The multicast address size is `MAXMACADDRLEN`.

## Risks

This is private state shared across DLS source files. Hash and reference management errors can leak or prematurely free link state. Zone ownership/reference fields require careful updates during link reassignment and destruction.
