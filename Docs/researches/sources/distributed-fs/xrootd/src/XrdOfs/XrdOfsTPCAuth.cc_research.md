# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCAuth.cc

## Purpose

`XrdOfsTPCAuth.cc` implements in-memory TPC rendezvous authorization. It lets an origin publish a grant, lets a destination fetch or wait for that grant, rejects duplicate/mismatched requests, expires stale entries, and replies asynchronously to clients blocked in wait-response.

## Important APIs, Types, and Functions

Implemented methods are `XrdOfsTPCAuth::Add`, `Del`, `Expired`, `Find`, `Get`, and `RunTTL`. Static state is `authMutex` and linked-list head `authQ`. The external thread entry `XrdOfsTPCAuthttl` invokes `RunTTL(0)`.

## Control Flow

`Add()` is called by the origin side. It builds the canonical origin ID, checks for a matching pending destination request, replies to that callback if present, or stores a new grant in `authQ`. `Get()` is called by the destination side. It removes a matching grant and returns it, rejects duplicate pending requests, or creates a pending callback entry and returns `SFS_STARTED`. `RunTTL(1)` starts the background TTL thread; `RunTTL(0)` loops forever scanning `authQ`, expiring entries, notifying callbacks, updating stats, and sleeping until the next expiration.

## State and Persistence Behavior

All authorization grants and pending requests are heap objects linked through `authQ`. Each object has an expiration time, inherited reference state, callback state in `Info`, and copied rendezvous strings. Entries are removed on match, delete, duplicate handling, or TTL expiry. Nothing persists across process restart.

## Dependencies and Integration Points

This implementation uses `XrdOfsTPCInfo` for matching and callbacks, `XrdOfsStats` for grant/expiry/error counters, `XrdSysMutex` for serialization, `XrdSysThread` for the TTL thread, `XrdSysTimer` for sleeping, and `XrdSfsInterface` return codes.

## Risks and Edge Cases

Duplicate authorization handling is security-sensitive: a duplicate grant without a pending callback is treated as protocol error, while duplicate pending destination requests are rejected and notified. `RunTTL()` sleeps based on `Cfg.maxTTL`; invalid zero or tiny TTL configuration could create noisy wakeups. `Del()` deletes under `authMutex`, so future destructor changes must avoid lock-order cycles.

## Test Signals

Tests should cover origin-before-destination, destination-before-origin, duplicate origin, duplicate destination, expiration with and without callbacks, reference-counted delete after successful `Get()`, and TTL thread startup failure logging.
