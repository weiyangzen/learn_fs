# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsageCheckFactory.java

## Purpose

This final utility class supplies `SpaceUsageCheckFactory` implementations for tests that need deterministic disk-capacity parameters without invoking real disk usage checks.

## Important APIs, Types, And Functions

`NONE` is a reusable no-op factory. `of(SpaceUsageSource, Duration, SpaceUsagePersistence)` creates a lambda factory returning `SpaceUsageCheckParams` for any directory. Nested `None` reports unlimited fixed capacity/available and disables persistence. Nested `HalfTera` reports 512 GiB capacity and available space. The private constructor prevents instantiation.

## Control Flow

Callers request params for a directory through a factory. The factory constructs `SpaceUsageCheckParams` with the supplied or fixed source, refresh period, and persistence strategy.

## State And Persistence

The utility itself is stateless. `None` and `HalfTera` use `SpaceUsagePersistence.None.INSTANCE`, so they deliberately do not persist usage. Factories returned by `of` close over caller-provided dependencies.

## Dependencies And Integration Points

It integrates with `SpaceUsageCheckFactory`, `SpaceUsageCheckParams`, `SpaceUsageSource`, `SpaceUsagePersistence`, and `MockSpaceUsageSource`.

## Risks

Tests using unlimited capacity can mask quota or overflow paths. `HalfTera` reports `used=0` because capacity equals available, so it is not suitable for tests requiring nonzero usage.

## Test Signals

Consumers should verify generated params preserve the target directory, source values, refresh duration, and persistence behavior.
