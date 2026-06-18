# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/CachingSpaceUsageSource.java

## Purpose

`CachingSpaceUsageSource` wraps another `SpaceUsageSource`, caches capacity/available/used values, and refreshes them periodically. It reduces expensive `du` calls and allows datanode volume code to adjust used space immediately after writes/deletes.

## Important APIs, Types, and Functions

Public methods include `start()`, `shutdown()`, `refreshNow()`, `incrementUsedSpace(long)`, `decrementUsedSpace(long)`, and `snapshot()`. Read/write synchronization uses Ratis `AutoCloseableReadWriteLock`. Refresh scheduling uses a daemon `ScheduledExecutorService`.

## Control Flow

Construction loads a persisted used value if present and always refreshes capacity/available from the source. `start()` schedules full used-space refreshes after a delay and available/capacity updates at up to one-minute intervals, or refreshes immediately when refresh is zero. `refresh()` is guarded by an `AtomicBoolean` so concurrent refreshes do not overlap.

## State and Persistence Behavior

Cached values are in memory. `shutdown()` calls `persistence.save(this)` before canceling scheduled tasks and shutting down the executor. `snapshot()` memoizes an immutable `Fixed` object until values change.

## Dependencies and Integration Points

It consumes `SpaceUsageCheckParams`, `SpaceUsageSource`, and `SpaceUsagePersistence`. Factories build it for datanode volumes.

## Risks and Test Signals

`refreshNow()` assumes an executor exists, so it is unsafe when refresh is zero. Increment/decrement clamp at zero/available but can diverge until the next source refresh. Tests should cover persistence load/save, scheduled startup, clamping warnings, snapshot invalidation, and refresh exception handling.
