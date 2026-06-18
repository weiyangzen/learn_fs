# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiRanges.cc

## Purpose
Provides the out-of-line lifetime methods for `XrdOssCsiRangeGuard`, the RAII object used by CSI page code to release page-range reservations and tracked-size locks.

## Important APIs and control flow
`ReleaseAll()` first releases a tracked-size lock if one is held, then removes the range from the owning `XrdOssCsiRanges` object and clears local pointers. `Wait()` asserts that the guard owns a range and delegates to `XrdOssCsiRanges::Wait()`. `unlockTrackinglen()` asserts that the guard has an associated `XrdOssCsiPages` object and calls `TrackedSizeRelease()`. The destructor calls `ReleaseAll()`, so normal scope exit cleans up both locking layers.

## State, dependencies, and integration
The file depends on `XrdOssCsiRanges.hh` for the guard/range definitions and `XrdOssCsiPages.hh` for tracked-size release. It does not persist state; it coordinates in-memory locks already acquired by page operations.

## Risks and test signals
Correctness depends on every successful `SetRange()` or `SetTrackingInfo(..., locked=true)` being paired with guard destruction or explicit `ReleaseAll()`. Assertions catch programmer misuse but disappear in release builds. Stress tests should issue overlapping read/write page operations, throw or early-return through guarded regions, and confirm no waiters remain blocked after errors.
