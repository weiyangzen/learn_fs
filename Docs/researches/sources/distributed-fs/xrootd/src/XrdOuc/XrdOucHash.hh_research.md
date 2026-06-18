# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucHash.hh

## Purpose
Declares a templated hash table with optional key/data ownership policies, replacement, lifetimes, and counted duplicate entries.

## Important APIs, Types, And Functions
`XrdOucHash_Options` defines `Hash_data_is_key`, `Hash_replace`, `Hash_count`, `Hash_keep`, `Hash_dofree`, and `Hash_keepdata`. `XrdOucHash_Item<T>` stores key, hash, data, expiry time, count, options, and next pointer. `XrdOucHash<T>` exposes `Add`, `Del`, `Find`, `Num`, `Purge`, `Rep`, and `Apply`, and includes implementation from `XrdOucHash.icc`.

## Control Flow
`Add` computes `XrdOucHashVal`, searches the bucket, optionally increments count, returns existing data unless replacing or expired, expands when load threshold is reached, and inserts a new item. `Find` removes expired entries. `Apply` scans all buckets, deletes expired or callback-negative entries, and stops on callback-positive entries. `Expand` grows table sizes by Fibonacci progression.

## State And Persistence
State is an in-memory bucket array and owned item nodes. Ownership behavior depends on options: keys may be duplicated or kept; data may be deleted, freed, kept, or aliased to key. No locking or persistence exists.

## Dependencies And Integration Points
Includes C allocation/string/time headers and external hash function `XrdOucHashVal`. Used widely by utility classes such as `XrdOucEnv` and `XrdOucGMap`.

## Risks And Test Signals
Risks include complicated ownership flags, no null checks after constructor allocation, no synchronization, counted delete semantics independent of the ignored `Del` option parameter, and exceptions thrown as integer `ENOMEM`. Test signals include replacement and expiry behavior, every ownership option combination under sanitizers, expansion rehashing, `Apply` deletion while iterating, and duplicate count add/delete cycles.
