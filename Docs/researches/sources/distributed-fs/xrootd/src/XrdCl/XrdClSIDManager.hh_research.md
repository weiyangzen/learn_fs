# sources/distributed-fs/xrootd/src/XrdCl/XrdClSIDManager.hh

## Purpose

This header declares the SID allocation manager and its pool. It provides the data structures used by XrdCl channels to allocate, time out, recycle, and share stream/request IDs.

## Important APIs, Types, And Functions

`SIDManager` exposes `AllocateSID`, `ReleaseSID`, `TimeOutSID`, `IsAnySIDOldAs`, `IsTimedOut`, `ReleaseTimedOut`, `ReleaseAllTimedOut`, `NumberOfTimedOutSIDs`, and `GetNumberOfAllocatedSIDs`. Private state includes allocation times, free SIDs, timed-out SIDs, the next ceiling, mutex, and pool refcount.

`SIDMgrPool` exposes singleton `Instance`, `GetSIDMgr(URL)`, and `Recycle(SIDManager*)`. `RecycleSidMgr` is the custom shared-pointer deleter. Copy/move construction and assignment are deleted.

## Control Flow

Consumers obtain managers through `SIDMgrPool::GetSIDMgr`, not by constructing `SIDManager` directly. Managers are private-constructed and friend-accessed by the pool. Returned shared pointers recycle managers back through the pool on destruction.

## State And Persistence Behavior

The header defines in-memory state only. Managers are keyed by channel ID in the pool and deleted when their internal refcount reaches zero.

## Dependencies And Integration Points

It depends on STL containers, `XrdSysPthread`, `Status`, and `URL`. It integrates with XRootD request multiplexing where SIDs are two-byte protocol fields.

## Risks And Edge Cases

The manager uses mutable mutex/refcount so const inspection methods still lock. Refcount is separate from `shared_ptr` control blocks because every returned shared pointer uses the same raw manager pointer with a custom deleter. Correct pool locking order is required to avoid deadlocks.

## Test Signals

Header/API tests should verify deleted copy operations, private construction, shared manager identity for equal channel IDs, distinct managers for distinct channel IDs, and safe destruction through the custom deleter.
