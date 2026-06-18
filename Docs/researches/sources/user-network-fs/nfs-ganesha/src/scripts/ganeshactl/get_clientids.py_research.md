# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/get_clientids.py

## Purpose

`get_clientids.py` is a CBSIM diagnostic script that introspects the callback simulator and prints known client IDs.

## Important APIs, Types, and Functions

Top-level code opens `dbus.SystemBus`, gets `/org/ganesha/nfsd/CBSIM`, calls `Introspect` through `dbus.INTROSPECTABLE_IFACE`, resolves `get_client_ids` on `org.ganesha.nfsd.cbsim`, and prints the result.

## Control Flow

The script performs all work at import/execution time with no argument parsing. It prints introspection XML first, then prints the client ID list returned by DBus.

## State and Persistence Behavior

It is read-only and persists nothing.

## Dependencies and Integration Points

It depends on `dbus` and the Ganesha CBSIM DBus object.

## Risks and Edge Cases

There is no exception handling, so DBus absence or method errors produce tracebacks. Printing full introspection data may be noisy for scripts consuming output. It is suitable for manual diagnostics, not stable machine parsing.

## Test Signals

Mock DBus tests should verify method lookup and printed sections. Integration tests require CBSIM support enabled in a Ganesha test instance.
