# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DUOptimizedFactory.java

## Purpose

`DUOptimizedFactory` creates optimized disk-usage params for volumes where metadata can be scanned separately and container data usage is supplied from memory.

## Important APIs, Types, and Functions

`setConfiguration` loads `DUFactory.Conf`. `paramsFor(File, Supplier<File>)` creates a `DUOptimized`, a `SaveSpaceUsageToFile` cache at `scmUsed`, and injects `params::getContainerUsedSpace` into the source.

## Control Flow

Callers must use the overload that supplies an exclusion provider. The plain `paramsFor(File)` currently returns `null`.

## State and Persistence Behavior

The factory stores only config. Generated params persist used-space cache in the volume directory.

## Dependencies and Integration Points

This is returned by `SpaceUsageCheckFactory.defaultImplementation()`, so datanode code must call the overload when using the default optimized factory.

## Risks and Test Signals

The `paramsFor(File)` null return is a sharp edge for generic callers and should be covered. Tests should verify default factory behavior, provider wiring, cache path, and container usage propagation.
