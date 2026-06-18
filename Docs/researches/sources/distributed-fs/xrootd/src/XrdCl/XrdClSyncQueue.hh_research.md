# sources/distributed-fs/xrootd/src/XrdCl/XrdClSyncQueue.hh

## Purpose

This header implements `SyncQueue<Item>`, a small blocking FIFO queue protected by an XRootD mutex and semaphore. It is a generic producer/consumer helper for thread handoff.

## Important APIs, Types, and Functions

`Put` pushes an item while holding `pMutex` and posts `pSem`. `Get` waits on the semaphore, locks, aborts if the queue is unexpectedly empty, pops, and returns the front item. `Clear` drops queued items and replaces the semaphore with a new zero-count semaphore. `IsEmpty` checks the queue under lock.

## Control Flow

Producers call `Put`; consumers block in `Get` until a posted item exists. The semaphore count mirrors queued item count unless `Clear` is called, which resets both queue contents and semaphore state.

## State and Persistence Behavior

State is in memory: `std::queue<Item>`, `XrdSysMutex`, and a heap-allocated `XrdSysSemaphore`. There is no persistence. Queue elements are copied by value.

## Dependencies and Integration Points

The class depends on `XrdSysPthread.hh` for mutex/semaphore primitives and C++ `std::queue`. It can be used by any XrdCl component that needs synchronous handoff without depending on the job manager.

## Risks and Edge Cases

`Clear` deletes and recreates the semaphore while only holding `pMutex`; a consumer already blocked in `Get` on the old semaphore can be stranded or race with deletion if external synchronization is not used. `Get` aborts the process on impossible semaphore/queue mismatch. There is no shutdown sentinel or timed wait.

## Test Signals

Tests should cover single and multiple producers/consumers, ordering, `IsEmpty`, and explicit `Clear` behavior only when no consumer is concurrently blocked.
