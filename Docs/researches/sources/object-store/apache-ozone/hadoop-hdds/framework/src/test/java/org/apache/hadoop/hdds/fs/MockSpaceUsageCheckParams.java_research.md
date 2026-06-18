# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsageCheckParams.java

## Purpose

This test helper provides a small builder for `SpaceUsageCheckParams`, making space-usage tests concise while defaulting to safe mock values.

## Important APIs, Types, And Functions

`newBuilder(File)` returns a `Builder`. The builder tracks `dir`, `source`, `refresh`, and `persistence`, and exposes `withSource`, `withRefresh`, `withPersistence`, and `build`. Defaults are unlimited usage source, zero refresh interval, and no persistence.

## Control Flow

Tests call `newBuilder(dir)`, override selected fields fluently, and call `build()` to create production `SpaceUsageCheckParams`.

## State And Persistence

Builder state is mutable and short-lived. Default persistence is disabled unless a test injects a `SpaceUsagePersistence`.

## Dependencies And Integration Points

It depends on production `SpaceUsageCheckParams` and test/source helpers `MockSpaceUsageSource` and `SpaceUsagePersistence.None`.

## Risks

The zero-refresh default changes `CachingSpaceUsageSource.start()` behavior compared with periodic production configs. Tests that rely on periodic scheduling must explicitly set a nonzero refresh.

## Test Signals

Signals are indirect through tests that assert constructed params carry expected directory, source, refresh, and persistence values.
