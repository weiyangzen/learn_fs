# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsageSource.java

## Purpose

This utility provides deterministic `SpaceUsageSource` instances for tests, including fixed values, unlimited capacity, and dynamic used-space from an `AtomicLong`.

## Important APIs, Types, And Functions

`unlimited()` returns a fixed source with `Long.MAX_VALUE` capacity and available. `fixed(capacity, available)` derives used as `capacity - available`. `fixed(capacity, available, used)` delegates to `SpaceUsageSource.Fixed`. `of(capacity, AtomicLong used)` returns an anonymous source whose used value is dynamic and whose available value is `capacity - used`.

## Control Flow

Tests construct a source and pass it into params, factories, or persistence checks. Production code calls `getUsedSpace`, `getCapacity`, and `getAvailable`.

## State And Persistence

Fixed sources are immutable. Dynamic sources read an external `AtomicLong` and do not persist changes themselves.

## Dependencies And Integration Points

It integrates with `SpaceUsageSource` and its `Fixed` implementation, and is used by multiple space-usage tests.

## Risks

Dynamic available space can become negative if the external used value exceeds capacity. `unlimited()` uses extreme values, so arithmetic in callers must avoid overflow.

## Test Signals

Signals are assertions of exact capacity, available, and used values before and after external atomic updates.
