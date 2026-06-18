# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmc.cc

## Purpose

`XrdRmc.cc` provides the public factory for the remanufactured memory cache.

## Important APIs, Types, And Functions

- `XrdRmc::Create(Parms&, XrdOucCacheIO::aprParms*)` constructs `XrdRmcReal`, deletes it on initialization failure, sets `errno`, and returns it as `XrdOucCache*`.

## Control Flow

The factory delegates all parameter validation and allocation to `XrdRmcReal`. The `rc` out parameter from the constructor determines success.

## State And Persistence

No static state is maintained here. Returned cache lifetime is owned by the caller through the `XrdOucCache` interface.

## Dependencies And Integration Points

It depends on `XrdRmc.hh` and `XrdRmcReal.hh`. It is the stable API entrypoint for users that do not need to know the concrete `XrdRmcReal` type.

## Risks And Edge Cases

- Constructor failure uses a partially constructed object plus `rc`; destructor behavior must be safe on failed initialization.
- `errno` is the only detailed error channel.

## Test Signals

Tests should create caches with default parameters, impossible allocation sizes, invalid page/cache sizes, and optional preread parameters, checking returned pointer and `errno`.
