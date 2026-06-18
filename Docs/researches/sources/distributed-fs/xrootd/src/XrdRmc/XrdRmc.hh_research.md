# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmc.hh

## Purpose

`XrdRmc.hh` declares the public memory-cache facade and parameter contract for a general `XrdOucCache` implementation over arbitrary `XrdOucCacheIO` sources.

## Important APIs, Types, And Functions

- `struct XrdRmc::Parms` defines `CacheSize`, `PageSize`, `Max2Cache`, `MaxFiles`, `Options`, `minPages`, and reserved fields.
- Option bits include `isServer`, `isStructured`, `canPreRead`, `logStats`, `Serialized`, `ioMTSafe`, and `Debug`.
- `XrdRmc::Create()` is the sole public factory.

## Control Flow

Consumers fill `Parms`, optionally provide automatic-preread parameters, call `Create()`, then attach `XrdOucCacheIO` objects through the returned cache. The detailed behavior described in comments maps to `XrdRmcReal` and `XrdRmcData`.

## State And Persistence

The header declares no static state. Cache state lives in the implementation returned by `Create()`.

## Dependencies And Integration Points

It includes `XrdOuc/XrdOucCache.hh` and is used by callers that want an in-memory, write-through, optionally structured/preread cache.

## Risks And Edge Cases

- Comments mention a maximum page size and write-in behavior, but the observed implementation mostly normalizes page size and currently uses write-through writes.
- Option semantics require careful caller coordination for `Serialized` and `ioMTSafe`; incorrect flags can create unnecessary locking or unsafe sharing.

## Test Signals

API tests should verify default parameter construction, option bit combinations, structured-file optimization, preread enablement, and write-through behavior via the `XrdOucCache` interface.
