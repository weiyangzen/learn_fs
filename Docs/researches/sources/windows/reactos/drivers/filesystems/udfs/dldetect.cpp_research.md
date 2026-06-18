# File Research: sources/windows/reactos/drivers/filesystems/udfs/dldetect.cpp

## Purpose

`dldetect.cpp` implements a debug deadlock detector for UDFS ERESOURCE acquisition. It wraps resource acquisition paths, records which thread is waiting for which resource, walks owner/waiter chains after repeated wait timeouts, and breaks into debug code when a cycle appears likely.

## Main Data

- `MaxThreadCount`: maximum number of tracked thread slots, supplied by `DLDInit`.
- `DLDThreadTable`: fixed array of `THREAD_STRUCT` entries mapping thread IDs to currently awaited resources plus source bug-check id/line.
- `DLDpTimeout`: four-second relative wait timeout used for periodic deadlock checks.
- `DLDpResourceTimeoutCount`: number of timed-out waits before graph inspection; initialized to `0x2`.
- `DLDThreadAcquireChain[DLD_MAX_REC_LEVEL]`: recursion trace for reported acquisition chains.

The detector is explicitly written for uniprocessor assumptions; `DLDInit` prints and breaks if `KeNumberProcessors > 1`.

## Initialization and Tracking

`DLDInit(ULONG MaxThrdCount)` initializes the timeout, stores the maximum table size, allocates `DLDThreadTable` from nonpaged pool, and zeros it.

`DLDFree()` frees the thread table.

`DLDAllocFindThread(ULONG ThreadId)` finds an existing table entry or reuses the first empty entry. If the table is full it prints a diagnostic and calls `BrutePoint`.

`DLDFindThread(ULONG ThreadId)` returns an existing tracked thread entry or `NULL`.

## Deadlock Detection Algorithm

`DLDpWaitForResource` waits on the resource's exclusive event or shared semaphore in four-second intervals. On each timeout, it increments a local wait counter. After the threshold, it calls `DLDProcessResource` while holding the resource spin lock.

`DLDProcessResource` inspects the supplied `ERESOURCE`:

- If the resource is not active, it returns no deadlock.
- If it is exclusively owned, or has a single shared owner in `OwnerThreads[1]`, it finds that owner thread and calls `DLDProcessThread`.
- If it has many owners, it iterates `OwnerTable` and processes every tracked owner.

`DLDProcessThread` checks whether the owner is the original waiter or appears in the current acquisition chain. If so, it prints a cycle diagnostic with bug-check id and source line data. Otherwise, if the owner thread is itself waiting on another resource, it recursively processes that resource.

The recursion limit is `DLD_MAX_REC_LEVEL` (40).

## Resource Acquisition Wrappers

`DLDAcquireExclusive(PERESOURCE, ULONG BugCheckId, ULONG Line)` manually acquires `Resource->SpinLock`, handles free resources, recursive exclusive acquisition by the same thread, and otherwise delegates to `DLDpAcquireResourceExclusiveLite`.

`DLDpAcquireResourceExclusiveLite(...)` allocates the `ExclusiveWaiters` event if needed, increments exclusive waiters, records the current thread's waiting resource and source location, releases the spin lock while waiting, then clears the waiting record and marks exclusive ownership after the wait returns.

`DLDAcquireShared(PERESOURCE, ULONG BugCheckId, ULONG Line, BOOLEAN WaitForExclusive)` manually handles free resources, recursive exclusive owner cases, shared owner table lookup/allocation, shared acquisition when no exclusive waiters are present, and waiting on `SharedWaiters` when necessary.

`DLDpFindCurrentThread(PERESOURCE, ERESOURCE_THREAD)` finds or allocates an owner entry for a thread in `OwnerThreads[0]`, `OwnerThreads[1]`, or the dynamically allocated `OwnerTable`. It can grow the owner table by allocating a new tagged table and copying old entries.

## Integration Points

`udfinit.cpp` initializes and frees the detector under debug/deadlock-detection configuration. `udf_dbg.cpp` routes debug resource acquisition wrappers to `DLDAcquireShared` and `DLDAcquireExclusive`. The public prototypes and helper structs are in `dldetect.h`.

## Notable Risks and Edge Cases

- This code directly reads and writes internal `ERESOURCE` fields and even writes to a hard-coded offset in the current thread object (`CurrentThread + 0x136`). That is highly version-specific and fragile outside the intended NT/ReactOS layout.
- The source only defines `DLDAcquireExclusive` and `DLDAcquireShared`; `dldetect.h` also declares `DLDAcquireSharedStarveExclusive` and `DLDUnblock`, which are not implemented in this file.
- The detector is explicitly not multiprocessor-safe by design, even though it uses spin locks around resource structures.
- Some diagnostic loop output in `DLDProcessThread` indexes `DLDThreadAcquireChain[i]` inside a loop over `j`, which appears suspicious for producing repeated or incorrect diagnostic rows.
- If allocation of waiter events/semaphores or owner tables fails, the code does not consistently propagate errors because the wrappers have `VOID` signatures.

## Testing Signals

Useful debug tests would deliberately create two-thread resource cycles, recursive exclusive acquisition, shared acquisition with and without exclusive waiters, owner-table growth beyond the two inline owner slots, timeout-only nondeadlock waits, and table-full conditions. Any modern port should also validate assumptions about `ERESOURCE` and thread-object layout.
