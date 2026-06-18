# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCache.hh

## Purpose
Declares the CMS in-memory path-location cache and its public manipulation/administrative API.

## Important APIs, Types, and Functions
Public members include `Paths`, `AddFile`, `DelFile`, `GetFile`, `UnkFile`, `WT4File`, `Bounce`, `Drop`, `Init`, and `TickTock`. Private state includes `Bhistory`, mutex, `XrdCmsNash` table, bounced array, valid-node vector, clocks, timeout/delay fields, hit/miss counters, and DFS mode.

## Control Flow
Callers update or query cache entries around locate/prepare workflows, while the background tick thread ages entries and scheduled recycle jobs reclaim them.

## State and Persistence Behavior
The cache is process-local, protected by `myMutex`, and never deleted. Entry lifetime is controlled by tick windows and optional nil timeout. No disk persistence.

## Dependencies and Integration Points
Includes scheduler/job, key/nash/path list/select/types, and pthread wrappers. Exposes global `XrdCms::Cache`.

## Risks and Edge Cases
The `Bounced` array is indexed by server number up to `STMax`; callers must bound server IDs. The global singleton complicates isolated tests. Time values mix seconds and tick windows.

## Test Signals
Compile tests should catch `SMask_t`, `STMax`, and key API drift. Unit tests should validate constructor defaults and public method contracts.
