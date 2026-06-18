# sources/user-network-fs/samba/source4/lib/socket/netif.h

## Purpose

`netif.h` is the small include aggregator for the source4 socket network-interface helpers.

## Important APIs, Types, and Functions

It includes system networking declarations, `lib/socket/interfaces.h`, and generated `lib/socket/netif_proto.h`. The actual interface structure and functions are implemented in `interface.c` and exposed through the included prototype header.

## Control Flow

There is no runtime control flow. Translation units include this header to get interface helper declarations and required socket/network types.

## State and Persistence Behavior

The header defines no state. Runtime state is the talloc-owned interface list managed by `interface.c`.

## Dependencies and Integration Points

It bridges system network headers with Samba socket interface/prototype headers. `interface.c` includes it directly, and callers of network interface helpers depend on the prototypes it aggregates.

## Risks and Edge Cases

Because this is an aggregator, stale or missing generated `netif_proto.h` would break compile consumers. Include ordering matters if platform network types are not available before the generated prototypes.

## Test Signals

Compile coverage of `interface.c` and callers validates this header. Runtime behavior is covered by tests for `load_interface_list()` and query helpers.

Source-read signal: reviewed complete local file (24 lines).
