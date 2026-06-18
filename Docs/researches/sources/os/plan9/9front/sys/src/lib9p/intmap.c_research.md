# File Research: sources/os/plan9/9front/sys/src/lib9p/intmap.c

## Read Status
Complete: 164 lines read.

## Purpose
Provides a small thread-safe integer-keyed map used by fid and request pools.

## Main Responsibilities
- Store `ulong` ids to arbitrary pointers.
- Provide insert, conditional insert, lookup, delete, and full-map free.
- Increment object references on lookup through a caller-supplied callback.
- Protect table structure with an `RWLock`.

## Important Functions
- `allocmap`: creates a map and installs an optional increment callback.
- `freemap`: destroys all buckets and optionally calls a destroy callback for values.
- `lookupkey`: finds a value and calls `inc` while holding the read lock.
- `insertkey`: inserts or replaces an id, returning the old value.
- `caninsertkey`: inserts only if the id is absent.
- `deletekey`: removes an id and returns its value.

## Data Structures
- `Intmap`: `RWLock`, fixed 128-bucket hash table, and `inc` callback.
- `Intlist`: bucket-chain node containing id, value, and next link.

## Dependencies and Interactions
- Used by `fid.c` and `req.c`.
- The comment clarifies that value reference increments must be independently safe because they happen while the map lock is held.
