# sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFCache.hh

## Purpose

This header declares the password-file entry cache used by XrdSut security code. It combines cache-wide read/write locking, per-entry mutex references, hash lookup, backing-file metadata, and cache-management APIs.

## Important APIs, types, and functions

`XrdSutPFCacheRef` tracks and unlocks a held entry mutex. `XrdSutPFCache` exposes status methods `Entries` and `Empty`, lifecycle methods `Init`, `Reset`, `Load`, `Flush`, `Refresh`, `Rehash`, `SetLifetime`, cache operations `Get`, `Add`, `Remove`, `Trim`, and debug `Dump`. Private helpers perform raw lookup and deferred-safe deletion.

## Control flow

Callers generally create a ref, call `Get` or `Add`, use the returned locked entry, then let the ref unlock. File-backed callers load or refresh from an `XrdSutPFile` and flush modified entries back.

## State and persistence behavior

The header defines in-memory state plus optional backing file path. Persistence happens through the implementation's `Load`/`Flush`/`Refresh` methods and `XrdSutPFile`.

## Dependencies and integration points

It depends on protocol integer types, `XrdSutPFEntry`, `XrdOucHash`, `XrdOucString`, and XrdSys locks. `XrdSecpwd` uses this cache for credential and public-key file data.

## Risks and edge cases

The API returns raw mutable entry pointers protected by an external ref object; forgetting the ref or keeping the pointer after unlock is unsafe. `Entries` returns `cachemx + 1`, which includes holes after removals and is not active-entry count. `Get(int)` only checks upper bound, not negative indices.

## Test signals

Header/API tests should cover ref locking/unlocking, empty state, index lookup boundaries, active-entry holes after removal, and integration with file-backed load/flush.
