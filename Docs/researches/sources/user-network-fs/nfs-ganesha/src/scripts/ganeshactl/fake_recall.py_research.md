# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/fake_recall.py

## Purpose

`fake_recall.py` is a CBSIM test/diagnostic helper that asks the Ganesha callback simulator to trigger a fake delegation recall for a client ID.

## Important APIs, Types, and Functions

`usage()` prints expected syntax. `main()` parses arguments with `getopt`, connects to `/org/ganesha/nfsd/CBSIM`, prints introspection data, obtains `fake_recall` from `org.ganesha.nfsd.cbsim`, and calls it with `dbus.UInt64(clientid)`.

## Control Flow

The script expects one client identifier, then performs DBus object lookup and method invocation. `getopt.GetoptError` prints usage. The callback simulator response is printed directly.

## State and Persistence Behavior

The script persists nothing locally. It may trigger server-side callback simulator behavior and affect test client/delegation state.

## Dependencies and Integration Points

It depends on `dbus`, `getopt`, and a daemon exposing `org.ganesha.nfsd.cbsim` at `/org/ganesha/nfsd/CBSIM`.

## Risks and Edge Cases

Argument handling is flawed: `getopt.getopt` returns `(opts, args)`, so `clientid = args[0]` stores a list rather than the first remaining argument. Passing that to `dbus.UInt64` likely fails. There is no DBus exception handling around object lookup or method call.

## Test Signals

Argument parser tests should verify a numeric client ID reaches `dbus.UInt64`. DBus mock tests should cover introspection and fake recall success/failure.
