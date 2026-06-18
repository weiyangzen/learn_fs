# sources/distributed-fs/xrootd/src/XrdSut/XrdSutCache.hh

## Purpose

This header implements a generic in-memory cache for `XrdSutCacheEntry` objects, protected by a recursive table mutex and per-entry read/write locks. It is a template-like concrete cache used by security utility code for short-lived validated entries.

## Important APIs, types, and functions

`XrdSutCacheGet_t` is an optional condition predicate, and `XrdSutCacheArg_t` is a four-slot generic argument carrier. `XrdSutCache::Get(tag)` returns an existing entry read-locked. `Get(tag, rdlock, condition, arg)` returns an existing entry read-locked if valid by condition, otherwise write-locked for refresh, or creates a new write-locked entry. `Num` returns table count and `Reset` purges the hash table.

## Control flow

Each lookup locks the hash table, finds or creates an entry, then obtains the entry lock before returning. The conditional lookup first read-locks an existing entry and applies the predicate; failed predicates cause an unlock followed by write-lock acquisition so the caller can validate/update the entry. The `rdlock` output tells the caller which lock mode was obtained.

## State and persistence behavior

State is fully in-memory: an `XrdOucHash<XrdSutCacheEntry>` plus locks. There is no disk persistence. Returned entries remain locked until the caller unlocks `entry->rwmtx`, usually via `XrdSutCERef`.

## Dependencies and integration points

The header depends on `XrdOucHash`, `XrdSutCacheEntry`, and XrdSys pthread locks. It complements the file-backed `XrdSutPFCache` but stores generic `XrdSutCacheEntry` records.

## Risks and edge cases

The table mutex is held while entry locks are acquired, so lock ordering must remain consistent to avoid deadlocks. If entry locking fails, the entry status is set inactive but still returned in some paths. `Reset` purges the table without taking the table mutex in this inline implementation, so external synchronization expectations should be checked. Callers must always unlock returned entries.

## Test signals

Concurrency tests should cover simultaneous first lookup, condition pass/fail, lock failure simulation, reset under use, and correct `rdlock` reporting. Leak tests should verify purged entries are destroyed by the hash table policy.
