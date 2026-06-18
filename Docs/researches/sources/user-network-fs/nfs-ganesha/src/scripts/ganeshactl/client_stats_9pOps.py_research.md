# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/client_stats_9pOps.py

## Purpose

This script prints nonzero 9P operation counters for a specific client IP address using the Ganesha client statistics DBus interface.

## Important APIs, Types, and Functions

There are no reusable functions. Top-level code binds `dbus.SystemBus`, gets `/org/ganesha/nfsd/ClientMgr`, resolves `Get9pOpStats` on `org.ganesha.nfsd.clientstats`, validates one positional `client_ipaddr`, iterates `OpNames`, and prints totals.

## Control Flow

After connecting to DBus, the script requires exactly one argument. For each hard-coded 9P op name, it calls `Get9pOpStats(client_ipaddr, opname)`. If the returned status is false it prints the error and stops; otherwise it prints the op name and total when `opstats[3][0]` is nonzero.

## State and Persistence Behavior

The script is read-only and stores no state. It observes live counters from the daemon.

## Dependencies and Integration Points

It depends on Python `dbus` and the Ganesha DBus clientstats interface. It is a standalone diagnostic utility.

## Risks and Edge Cases

The op-name list is hard-coded and must match server-side names. All DBus reply fields are positional. A broad exception around object lookup hides exact connection errors. It performs no IP address validation beyond accepting a string.

## Test Signals

Tests should mock `Get9pOpStats` for zero, nonzero, and error replies and verify printed output. Integration tests require a daemon with 9P stats enabled.
