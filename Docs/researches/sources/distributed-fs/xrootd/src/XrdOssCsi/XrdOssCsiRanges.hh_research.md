# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiRanges.hh

## Purpose
Defines the page-range locking primitive used by the CSI checksum layer to serialize overlapping mutations while allowing non-overlapping operations and compatible read-only overlaps.

## Important APIs and types
`XrdOssCsiRange_s` stores an inclusive page range, a read-only flag, the count of earlier overlapping blockers, its own mutex/condition variable, and a free-list link. `XrdOssCsiRangeGuard` owns a registered range and optional tracked-size lock, exposes `Wait()`, `ReleaseAll()`, `unlockTrackinglen()`, and records the tracked-size pair seen by the caller. `XrdOssCsiRanges` maintains `ranges_` plus a recycled allocation list.

`AddRange()` counts overlapping non-compatible existing ranges, allocates a range record, pushes it to the active list, and arms the guard. `Wait()` blocks on the range's condition variable until `nBlockedBy` reaches zero. `RemoveRange()` erases a completed range, decrements blocker counts for later overlapping ranges, notifies newly unblocked ranges, and recycles the node.

## State, dependencies, and integration
State is purely in-memory and protected by `rmtx_` plus per-range mutexes. It depends on C++ mutex/condition-variable primitives and `XrdSysPthread.hh`. CSI page read/write code integrates it with tracked-size locking in `XrdOssCsiPages`.

## Risks and test signals
The active-list algorithm assumes ranges are removed exactly once and that compatibility only exists for read-only/read-only overlaps. Recycled nodes must not retain stale counters or flags after `AddRange()` reinitializes them. Tests should cover multiple waiters, read-only sharing, writer after readers, readers after writer, and destruction while waiters are pending.
