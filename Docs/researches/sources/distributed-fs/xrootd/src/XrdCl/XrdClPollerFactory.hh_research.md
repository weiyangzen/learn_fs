# sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerFactory.hh

## Purpose

This header declares the small factory responsible for creating `Poller` implementations from a runtime preference string.

## Important APIs, Types, And Functions

`PollerFactory` exposes one static method: `CreatePoller(const std::string &preference)`. It returns a newly allocated `Poller*` or null if no preferred implementation is known.

## Control Flow

The header defines the contract only. The `.cc` implementation parses a comma-separated preference list and picks the first available backend.

## State And Persistence Behavior

No state is declared. Ownership of returned pollers belongs to the caller.

## Dependencies And Integration Points

The header includes `XrdClPoller.hh` and is used by `PostMaster` during initialization. It decouples environment configuration from concrete poller classes.

## Risks And Edge Cases

Because the API returns a raw pointer, callers must delete the poller on failure paths and final shutdown. A null return is a hard startup failure for client networking.

## Test Signals

Compile-time tests should include the header from PostMaster-like code; runtime tests belong to the implementation and should verify null handling by `PostMaster::Initialize`.
