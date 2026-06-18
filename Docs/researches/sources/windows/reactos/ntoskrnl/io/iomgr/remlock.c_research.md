# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/remlock.c

## Role

`remlock.c` implements WDM remove-lock helpers. Remove locks prevent device removal while I/O is active and optionally track debug acquisition tags, source locations, high-water marks, and lock hold duration.

## Main entry points and behavior

- `IoInitializeRemoveLockEx()` initializes either a debug remove lock or common remove lock, setting signature, high watermark, maximum locked ticks, allocation tag, spin lock, tracking list, removed flag, initial `IoCount` of 1, and the remove event (lines 31-73).
- `IoAcquireRemoveLockEx()` increments `IoCount`; if the device is not removed and debug tracking is enabled, it allocates a tracking block tagged with the caller's tag/file/line and acquisition tick count, linking it under the debug spin lock. If already removed, it undoes the increment, signals the event if count becomes zero, and returns `STATUS_DELETE_PENDING` (lines 78-142).
- `IoReleaseRemoveLockEx()` removes one matching debug tracking block for the tag, checks all tracked blocks for excessive hold time, accounts for low-memory tracking failures, decrements `IoCount`, and signals `RemoveEvent` when the count reaches zero after removal (lines 147-236).
- `IoReleaseRemoveLockAndWaitEx()` marks the lock removed, decrements the count, waits for outstanding holders, and releases the final debug tracking block (lines 241-288).

## Data and synchronization

Debug tracking blocks are singly linked through `Lock->Dbg.Blocks` and protected by `Lock->Dbg.Spin`. The common lock count is maintained with interlocked operations. `RemoveEvent` is a synchronization event signaled when the outstanding count reaches zero.

## Implementation gaps and risks

- `IoInitializeRemoveLockEx()` intentionally falls through from the debug-size case into common initialization; this matches the structure layout pattern but lacks an explicit `break`, so future edits must preserve this dependency (lines 52-72).
- `IoReleaseRemoveLockAndWaitEx()` decrements `IoCount` twice: once into `LockValue`, then again in the wait condition (lines 254-260). This is a high-risk semantic detail because the usual remove-lock algorithm releases the caller's acquisition and waits for remaining counts without accidentally dropping an extra reference.
- The debug tag mismatch assertion in `IoReleaseRemoveLockAndWaitEx()` asserts `TrackingBlock->Tag != Tag` after detecting inequality, which appears inverted for a failure assertion and would not catch the mismatch in the usual way (lines 277-283).
- When debug tracking allocation fails, release attempts consume `LowMemoryCount` instead of requiring a matching tag; this is intentional fallback behavior but can hide tag-pairing mistakes during memory pressure (lines 103-109, 208-221).
