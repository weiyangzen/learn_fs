# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/grace_period.py

## Purpose

`grace_period.py` is a small command-line helper that triggers a Ganesha grace period for a supplied client IP address over DBus.

## Important APIs, Types, and Functions

Top-level code reads `sys.argv[1]`, opens `dbus.SystemBus`, gets `/org/ganesha/nfsd/admin`, resolves `grace` on `org.ganesha.nfsd.admin`, and prints the result.

## Control Flow

The script prints `event:ip_addr=...`, connects to DBus, prints "Start grace period.", calls `grace(ipaddr)`, and exits with an error message if DBus object lookup or method call fails.

## State and Persistence Behavior

There is no local persistence. The remote daemon enters a grace behavior for the provided IP/client.

## Dependencies and Integration Points

It depends on `dbus` and the Ganesha admin DBus interface. It may be used by event hooks or operator scripts.

## Risks and Edge Cases

It indexes `sys.argv[1]` without checking argument count. IP addresses are not validated. Error messages hide the underlying DBus exception detail.

## Test Signals

Tests should cover missing argument handling, DBus unavailable behavior, and successful `grace` invocation with a mocked admin object.
