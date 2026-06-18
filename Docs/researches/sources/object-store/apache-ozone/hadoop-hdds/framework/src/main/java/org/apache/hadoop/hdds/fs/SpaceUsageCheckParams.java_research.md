# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsageCheckParams.java

## Purpose

`SpaceUsageCheckParams` bundles all parameters needed by `CachingSpaceUsageSource`: directory, underlying source, refresh period, persistence, and optional container usage supplier.

## Important APIs, Types, and Functions

The constructor validates non-null parameters and non-negative refresh. Accessors expose `dir`, canonical `path`, `source`, `refresh`, and `persistence`. `setContainerUsedSpace` and `getContainerUsedSpace` support optimized DU composition.

## Control Flow

Construction resolves the directory canonical path and throws `UncheckedIOException` on failure. Container usage defaults to a supplier returning zero until explicitly set.

## State and Persistence Behavior

State is in-memory configuration. Persistence behavior is delegated to the supplied `SpaceUsagePersistence`.

## Dependencies and Integration Points

Factories create params; `CachingSpaceUsageSource` consumes them; `DUOptimizedFactory` uses the container supplier bridge.

## Risks and Test Signals

The container supplier is mutable and not explicitly synchronized. Zero refresh is allowed here but incompatible with `SaveSpaceUsageToFile` expiry rules if paired incorrectly. Tests should cover validation, canonical path failures, default container usage, and setter behavior.
