# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMsg.hh

## Purpose
Declares the outstanding-message slot used by CMS clients to wait for manager replies.

## Important APIs, Types, and Functions
Public API includes static `Alloc`, `Init`, `inQ`, and `Reply`; instance methods include `ID`, `getResult`, `Lock`, `UnLock`, `Wait4Reply`, and `Recycle`. Constants define a 1024-slot table with generation increments.

## Control Flow
Callers allocate a locked message slot, send its `ID()` as the stream ID, wait on `Wait4Reply()`, read `getResult()`, then recycle. Manager receive code calls static `Reply()` to match and signal the slot.

## State and Persistence Behavior
Each slot stores a next pointer, condition variable, waiting flag, ID, response pointer, and decoded result. Static free-list/table state is process lifetime.

## Dependencies and Integration Points
Includes CMS protocol headers and pthread primitives; forward-declares `XrdOucErrInfo` and `XrdOucBuffer`. Integrated with `XrdCmsClientMan` and `XrdCmsParser`.

## Risks and Edge Cases
The fixed slot count is a hard concurrency limit. Correctness depends on callers respecting lock ownership comments: `Alloc()` and `RemFromWaitQ()` return locked objects, and `Recycle()` expects the lock to be held.

## Test Signals
Tests should check lock/wait/recycle protocol, fixed-capacity failure, and stale generation handling.
