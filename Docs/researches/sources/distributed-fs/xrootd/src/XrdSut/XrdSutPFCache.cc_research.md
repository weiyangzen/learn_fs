# sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFCache.cc

## Purpose

This file implements `XrdSutPFCache`, an in-memory cache of password-file entries (`XrdSutPFEntry`) with optional load/flush/refresh from an `XrdSutPFile`. It accelerates security credential lookups while preserving entry-level locking.

## Important APIs, types, and functions

Implemented methods include destructor, `Init`, public and private `Get`, `Add`, `Remove`, `Delete`, `Trim`, `Reset`, `Dump`, `Load`, `Rehash`, `Flush`, and `Refresh`. `Delete` also manages a static deferred-delete queue for entries that cannot be locked immediately.

## Control flow

`Init` allocates the pointer array and initializes the hash table. Public `Get` refreshes the hash if stale, read-locks the cache, finds exact or best wildcard entry, then repeatedly tries to lock the entry mutex, waiting up to `maxTries * retryMSW`. `Add` returns an existing locked entry if present, otherwise write-locks the cache, expands the array when full, appends a new entry, rehashes, and returns it locked through `XrdSutPFCacheRef`. `Load` reads a `PFile` header and index chain, reads active entries, copies them into cache entries, and rebuilds the hash. `Flush` writes newer cache entries back to a file.

## State and persistence behavior

The cache stores an array of `XrdSutPFEntry *`, current capacity/highest index, update timestamps, lifetime, a hash table mapping names to array indices, the backing file path, and initialization state. Persistence is optional and mediated by `XrdSutPFile`: `Load` populates from disk, `Flush` writes newer cache values, and `Refresh` reloads when the backing file is newer.

## Dependencies and integration points

The file depends on `XrdSutPFile`, `XrdSutPFEntry`, `XrdSutAux`, XrdSut tracing, `XrdOucHash`, XrdSys locks, and `XrdSysTimer`. It is used by XrdSec password protocol caches for admin, user, autologin, and server-public-key data.

## Risks and edge cases

There are several high-risk areas. `Init` sets `isinit = 1` on the allocation-failure path rather than the success path, which can cause repeated initialization attempts after success or false initialized state after failure. The expansion loop that should clear new array slots uses `for (i = cachemx + 1; i <= cachemx; i++)`, so it never initializes the new tail. `Remove(opt==1)` dereferences the hash lookup result without checking null. `Refresh` takes the cache write lock and then calls `Load`, which also write-locks; this depends on lock implementation behavior and may deadlock if non-recursive. Deferred deletion is a static queue shared across cache instances, so cleanup in one cache can process entries from another. Time comparisons use cache update time rather than exact file mtimes, so rapid file updates may be missed on coarse timestamp filesystems.

## Test signals

Tests should cover init success/failure, add beyond initial capacity, exact and wildcard get, entry-lock contention and retry timeout, remove missing/existing/prefix entries, deferred delete cleanup, trim by lifetime, load/flush/refresh round trips, null hash lookup paths, and concurrent use by multiple threads.
