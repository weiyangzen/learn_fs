# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCache.cc

## Purpose
Implements the CMS path-location cache used to remember which servers have, might have, or are being queried for a file, and to dispatch waiting requests when location data arrives.

## Important APIs, Types, and Functions
Defines global `XrdCms::Cache`, local scheduled `XrdCmsCacheJob`, and tick thread entry `XrdCmsStartTickTock`. Public methods implemented are `AddFile()`, `DelFile()`, `GetFile()`, `UnkFile()`, `WT4File()`, `Bounce()`, `Drop()`, `Init()`, and `TickTock()`. Private helpers are `Add2Q()`, `Dispatch()`, `getBVec()`, and `Recycle()`.

## Control Flow
`AddFile()` creates or updates path entries and dispatches read/write wait queues when enough location data is known. `GetFile()` returns current vectors, invalidating entries affected by server bounce clocks and query deadlines. `WT4File()` attaches callback info to an entry when clients should wait. `TickTock()` advances the cache clock, unloads expired entries, and schedules asynchronous recycle jobs.

## State and Persistence Behavior
All state is in memory: `XrdCmsNash` cache table, path anchor, valid server vector, bounce history, tick clock, nil-entry timeout, query/deadline settings, wait queues, and statistics. No durable cache exists; cluster events repopulate it.

## Dependencies and Integration Points
Depends on `XrdCmsKey`, `XrdCmsNash`, `XrdCmsSelect`, `XrdCmsRRQ`, scheduler jobs, timers, and mutexes. Integrates with server bounce/drop events and request callback queues.

## Risks and Edge Cases
Cache correctness depends on `TODRef` fast-path validation and bounce-clock math. `nilTMO` is raised to avoid infinite lookup delay but can still retain negative entries. Shared-everything vs shared-nothing dispatch behavior differs substantially. The fixed message in `Recycle()` reports cache allocator state and can be noisy under churn.

## Test Signals
Tests should cover add/update/delete semantics, pending vs online vectors, stale bounce invalidation, wait queue dispatch for read/write paths, DFS vs non-DFS dispatch, nil timeout expiry, tick unload/recycle behavior, and server drop removal.
