# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DUOptimized.java

## Purpose

`DUOptimized` combines shell `du` of metadata paths with in-memory container data usage. It avoids scanning large container data trees when datanode container accounting already knows their sizes.

## Important APIs, Types, and Functions

The constructor creates a `DU` with an exclusion provider. `setContainerUsedSpaceProvider(Supplier<Supplier<Long>>)` links to params-held container usage. `getUsedSpace()` returns metadata `du` plus supplied container usage when configured.

## Control Flow

Every used-space check runs `metaPathDU.getUsedSpace()`. If no provider exists, it returns metadata size only. Otherwise it calls the outer supplier to obtain a current inner supplier, reads container usage, logs both components, and sums them.

## State and Persistence Behavior

State is in-memory: the underlying metadata `DU` and optional provider. Persistence is external through factory-created params.

## Dependencies and Integration Points

It implements `SpaceUsageSource` and delegates capacity/available to `DU`. `DUOptimizedFactory` wires the provider from `SpaceUsageCheckParams`.

## Risks and Test Signals

The nested supplier shape is easy to misuse and may throw at runtime if the container provider is absent or not thread-safe. Tests should verify metadata-only behavior, summed usage after provider injection, and exception propagation from either component.
