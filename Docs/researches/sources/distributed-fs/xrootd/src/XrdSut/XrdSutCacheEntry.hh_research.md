# sources/distributed-fs/xrootd/src/XrdSut/XrdSutCacheEntry.hh

## Purpose

This header declares generic cache-entry storage for XrdSut in-memory caches, including entry status values, four arbitrary buffers, metadata, and a read/write lock.

## Important APIs, types, and functions

`kCEntryStatus` defines inactive, disabled, allowed, expired, ok, and special states. `XrdSutCacheEntryBuf` owns one byte buffer. `XrdSutCacheEntry` stores name, status, count, modification time, four buffers, and `rwmtx`. `Length`, `Reset`, `SetName`, `AsString`, and assignment are the main entry APIs. `XrdSutCERef` is an RAII-ish lock holder for `XrdSysRWLock`.

## Control flow

Callers obtain entries through `XrdSutCache`, use the lock already held or manage it through `XrdSutCERef`, inspect/update fields, then unlock. The header exposes fields publicly for direct consumer mutation.

## State and persistence behavior

No direct persistence. The `Length` calculation describes a serializable shape similar to `XrdSutPFEntry`, but this cache entry is used in memory.

## Dependencies and integration points

It depends on protocol integer types and XrdSys pthread locks. It is consumed by `XrdSutCache.hh`.

## Risks and edge cases

Public fields and manual lock management can lead to races if callers bypass the cache's returned lock. `XrdSutCERef::Set` unlocks a prior lock when switching, which is convenient but can hide accidental lock replacement. Copying entries does not copy lock state, as expected, but assignment behavior must be validated in the source.

## Test signals

Tests should validate lock holder behavior, buffer ownership, length calculation for all buffer combinations, status transitions, and field updates under read/write locks.
