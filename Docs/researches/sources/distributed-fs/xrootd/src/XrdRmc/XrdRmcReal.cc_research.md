# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcReal.cc

## Purpose

`XrdRmcReal.cc` implements the actual shared memory cache behind RMC. It owns page memory, slot metadata, file attachment tracking, hash tables, LRU lists, preread worker threads, and cache page fault/ref/update/truncation operations.

## Important APIs, Types, And Functions

- Constructor normalizes parameters, allocates anonymous `mmap` memory for data plus a hash table, allocates `XrdRmcSlot` metadata, initializes page LRU, file-slot free lists, and optional preread threads.
- Destructor waits for attached files to detach, stops preread threads, deletes slots, and unmaps cache memory.
- `Attach(ioP, Opts)` maps an `XrdOucCacheIO` to a file slot and returns an `XrdRmcData` wrapper, reusing one wrapper for duplicate attachments.
- `Detach(ioP)` drops an I/O attachment, releases all page slots owned by the file when the final reference disappears, and signals destructor waiters.
- `Get(ioP, lAddr, rAmt, noIO)` is the central page lookup/fault method. It handles hits, in-transit waits, free-slot selection, owner/hash removal, underlying reads, waiter wakeup, and slot initialization.
- `Ref()`, `Upd()`, and `Trunc()` release references, update cached writes, and invalidate cached pages.
- `PreRead()` worker loop and `PreRead(prTask*)` queue preread work.
- `ioAdd()`, `ioDel()`, `ioEnt()`, and `ioLookup()` track attached underlying I/O objects.

## Control Flow

Initialization computes a power-of-two segment size, segment count, maximum cached read size, and file-slot capacity. The page data area is anonymous memory; slots `1..SegCnt-1` form the LRU pool, while slots from `SegCnt` onward track attached file objects. Preread threads wait on `prReady`.

`Get()` first checks the hash bucket for a logical address. If a slot is in transit, the caller waits on a stack semaphore linked into the slot wait queue. On a miss with an I/O object, the least-recent free slot is pulled, detached from prior ownership/hash state, marked in transit, and filled by reading from the underlying object without holding the cache mutex. Waiters are posted before the caller returns the buffer. `Ref()` later marks consumption, adjusts single-use/LRU behavior, and indicates EOF state to sequential readers.

Deletion is cooperative. The destructor blocks on `AZero` until `Attached` reaches zero; preread worker shutdown is then coordinated with `prStop` and semaphore chaining.

## State And Persistence

All cache state is in process memory: `Base` mmap data, `Slash` content hash, `Slots`, file hash table `hTab`, free file-slot list, attach counts, LRU/owner lists, debug flags, and preread queue/thread counters. There is no durable persistence.

## Dependencies And Integration Points

It depends on POSIX `mmap/munmap`, pthread-style XRootD thread helpers, `XrdRmcData`, `XrdRmcSlot`, and `XrdOucCache`. It is created only through `XrdRmc::Create()` and serves `XrdRmcData` wrappers.

## Risks And Edge Cases

- Destructor calls `delete Slots` for an array allocated with `new[]`, which is a correctness risk.
- `munmap()` uses only `SegSize * SegCnt`, while allocation included `SegCnt * sizeof(int)` for the hash table, potentially leaving the trailing mapping length inconsistent.
- `ioEnt()` hashes pointer bytes through a union with four shorts, which is pointer-size sensitive and dated.
- In-transit waiter logic depends on stack semaphore lifetime and precise wakeup ordering under the cache mutex.
- Failed I/O frees the slot and wakes waiters, which then detect changed contents as `-EIO`.
- Cache capacity/lifetime behavior relies on `XrdRmcSlot` list invariants; list corruption would be hard to diagnose.

## Test Signals

Tests should cover parameter normalization, allocation failure, attach/detach reference counting, duplicate attachment reuse, cache hit/miss/fault behavior, simultaneous readers of the same missing page, read error propagation, LRU eviction, truncation invalidation, write update, preread thread shutdown, and destructor with live attachments.
