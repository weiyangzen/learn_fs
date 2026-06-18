# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DedicatedDiskSpaceUsage.java

## Purpose

`DedicatedDiskSpaceUsage` is a fast `SpaceUsageSource` for volumes assumed to own their entire filesystem. It estimates used space as total capacity minus usable space.

## Important APIs, Types, and Functions

`getUsedSpace()` times `calculateUsedSpace()`. `calculateUsedSpace()` returns `getCapacity() - getFile().getUsableSpace()`.

## Control Flow

There is no traversal. Each usage query reads filesystem-level capacity and usable space from Java `File` APIs.

## State and Persistence Behavior

State is inherited immutable path data. No persistence is needed because checks are cheap.

## Dependencies and Integration Points

It extends `AbstractSpaceUsageSource` and is produced by `DedicatedDiskSpaceUsageFactory`.

## Risks and Test Signals

It is inaccurate when other data shares the filesystem, and usable space excludes some system-reserved space. Tests should verify arithmetic and construction behavior with temporary filesystems or mocked `File` behavior.
