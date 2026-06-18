# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/AbstractSpaceUsageSource.java

## Purpose

`AbstractSpaceUsageSource` is a convenience base for `SpaceUsageSource` implementations that measure usage for a filesystem path. It centralizes canonical-path handling, capacity/available reporting, and timing logs.

## Important APIs, Types, and Functions

The constructor stores the `File` and canonical path. `getAvailable()` delegates to `File.getUsableSpace()`, `getCapacity()` delegates to `File.getTotalSpace()`, and `time(LongSupplier, Logger)` measures and logs source-specific usage checks.

## Control Flow

Subclasses call `super(path)`, then implement `getUsedSpace()`, often by wrapping their calculation with `time`. Canonical-path resolution failures are converted to `UncheckedIOException`.

## State and Persistence Behavior

State is immutable: the original `File` and canonical path string. The class does not persist usage.

## Dependencies and Integration Points

It underpins `DU` and `DedicatedDiskSpaceUsage`, and implements common `SpaceUsageSource` behavior.

## Risks and Test Signals

Capacity and available values reflect Java filesystem APIs and can change between calls. Canonical path resolution can fail at construction. Tests should verify canonical path behavior, capacity/available delegation, and timing wrapper returning the supplier value.
