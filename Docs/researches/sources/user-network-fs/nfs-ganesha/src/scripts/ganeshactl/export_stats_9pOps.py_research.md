# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/export_stats_9pOps.py

## Purpose

This script prints nonzero 9P operation counters for a specific export ID using the Ganesha export statistics DBus interface.

## Important APIs, Types, and Functions

Top-level code binds `dbus.SystemBus`, gets `/org/ganesha/nfsd/ExportMgr`, resolves `Get9pOpStats` on `org.ganesha.nfsd.exportstats`, validates a numeric export ID, and iterates the same `OpNames` tuple used by the client variant.

## Control Flow

The script exits unless exactly one numeric argument is supplied. It converts the argument to `dbus.UInt16`, calls `Get9pOpStats(export_id, opname)` for each operation, stops on a false status, and prints op totals for nonzero counters.

## State and Persistence Behavior

It is read-only and stores no local state.

## Dependencies and Integration Points

It depends on Python `dbus` and the Ganesha exportstats DBus interface. It is a standalone stats diagnostic.

## Risks and Edge Cases

`dbus.UInt16(sys.argv[1])` relies on dbus-python accepting a string input; explicit `int()` would be safer. Export IDs outside 16-bit range are not checked. The hard-coded op list and positional reply parsing can drift from the server.

## Test Signals

Mock tests should cover usage errors, DBus object lookup failure, zero/nonzero operation counters, false status responses, and export ID conversion boundaries.
