# sources/user-network-fs/mergerfs/src/ugid.cpp

## Purpose
Defines thread-local UID/GID tracking variables used by credential switching helpers.

## Important APIs, Types, and Functions
The `ugid` namespace defines thread-local `currentuid`, `currentgid`, and `initialized`.

## Control Flow
There is no active flow in this file; inline functions in `ugid.hpp` read and update these variables.

## State and Persistence Behavior
State is per-thread process memory. It mirrors effective uid/gid after helper-managed changes and is not persisted.

## Dependencies and Integration Points
Includes `<unistd.h>` and backs `ugid::set()` and `ugid::SetGuard`.

## Risks and Edge Cases
Thread-local tracking can become wrong if code changes effective IDs outside `ugid::set()`. Initial values assume root until initialized.

## Test Signals
Test per-thread initialization, repeated set calls, restoration with guards, and interaction with external credential changes.
