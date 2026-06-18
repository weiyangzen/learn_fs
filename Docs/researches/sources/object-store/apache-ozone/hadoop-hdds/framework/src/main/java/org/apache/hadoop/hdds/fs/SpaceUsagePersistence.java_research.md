# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsagePersistence.java

## Purpose

`SpaceUsagePersistence` abstracts saving and loading cached disk usage values.

## Important APIs, Types, and Functions

`load()` returns an `OptionalLong`, and `save(SpaceUsageSource)` persists the current source usage. The nested `None` implementation is a singleton no-op used for cheap sources and tests.

## Control Flow

Implementations choose their own persistence mechanism. `None.load()` always returns empty and `None.save()` does nothing.

## State and Persistence Behavior

The interface has no state. `None` has no persistent state.

## Dependencies and Integration Points

`CachingSpaceUsageSource` invokes it on construction and shutdown. `SaveSpaceUsageToFile` is the primary file-backed implementation.

## Risks and Test Signals

Persistence implementations must avoid making shutdown fragile, because cache writes are advisory. Tests should cover `None` no-op behavior and integration load/save sequencing in `CachingSpaceUsageSource`.
