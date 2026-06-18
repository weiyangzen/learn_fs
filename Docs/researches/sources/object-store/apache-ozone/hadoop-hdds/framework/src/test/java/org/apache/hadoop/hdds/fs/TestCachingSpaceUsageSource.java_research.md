# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestCachingSpaceUsageSource.java

## Purpose

This class tests `CachingSpaceUsageSource`, covering initial values, refresh scheduling, persistence on shutdown, bounds handling for used/available updates, snapshot consistency, and thread naming.

## Important APIs, Types, And Functions

The tests use `CachingSpaceUsageSource`, `SpaceUsageCheckParams`, `SpaceUsageSource.snapshot`, `incrementUsedSpace`, `decrementUsedSpace`, `start`, `shutdown`, and `threadFactoryFor`. Helpers include `paramsBuilder`, `sameThreadExecutorWithoutDelay`, `verifyRefreshWasScheduled`, `assertAvailableWasUpdated`, and `assertSnapshotIsUpToDate`.

## Control Flow

Tests construct params with mock sources and persistence. Start behavior either refreshes once immediately when periodic refresh is disabled or schedules two fixed-delay tasks when refresh is configured. Mock executors run scheduled runnables synchronously, making refresh effects deterministic. Shutdown saves current usage, cancels scheduled futures, and shuts down the executor.

## State And Persistence

The subject caches used, capacity, and available values. Persistence is represented by `AtomicLong` through `MockSpaceUsagePersistence`. Boundary tests ensure usage never drops below zero and available never drops below zero while snapshots mirror current state.

## Dependencies And Integration Points

Dependencies include JUnit temp dirs, Mockito scheduled executor/futures, AssertJ, Commons `RandomUtils`, and the mock FS helpers in this package.

## Risks

The synchronous mock executor does not reveal concurrency races in scheduled refresh. Random initial values avoid constants but can complicate reproduction if an edge case depends on exact values. Two futures are expected on shutdown, tying the test to the implementation's dual refresh tasks.

## Test Signals

Signals include correct initial cached value, immediate or delayed schedule parameters, no early persistence before shutdown, saved shutdown value, clamped increments/decrements, ignored negative changes, fresh snapshots, and newline-free thread names ending with sequence numbers.
