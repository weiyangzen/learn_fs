# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/cpu-watcher-poll.py

## Purpose

This small Foolscap client polls a CPU watcher remote object for average CPU data and prints it.

## Important APIs, Types, and Functions

`fetch(furl)` creates a `Tub`, starts it, obtains a reference with `getReference`, calls remote `get_averages`, pretty-prints the result, and returns the Deferred. `oops` prints errors.

## Control Flow

The script schedules `fetch` from `eventual.fireEventually(sys.argv[1])`, attaches error and stop callbacks, and runs the Twisted reactor.

## State, Dependencies, Integration, Risks, and Tests

There is no persistence. Dependencies are Foolscap, Twisted reactor/eventual, and a watcher FURL argument. Integration is CPU watcher operations tooling. Risks include no argument validation, no timeout, and a Tub service that is not explicitly stopped. Tests should use a fake remote reference or Foolscap test tub to verify `get_averages`, formatting, and reactor shutdown on success/failure.
