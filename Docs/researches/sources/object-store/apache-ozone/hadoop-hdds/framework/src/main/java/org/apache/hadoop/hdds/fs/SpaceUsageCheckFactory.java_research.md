# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsageCheckFactory.java

## Purpose

`SpaceUsageCheckFactory` is the pluggable factory interface for datanode disk-usage sources. It allows deployments to choose accurate `du`, optimized `du`, or dedicated-disk accounting via configuration.

## Important APIs, Types, and Functions

`paramsFor(File)` is the core factory method; the overload accepting `Supplier<File>` supports exclusion paths. `create(ConfigurationSource)` loads `hdds.datanode.du.factory.classname`, reflects a no-arg factory, falls back to `defaultImplementation()`, and calls `setConfiguration`.

## Control Flow

Creation attempts class loading, constructor lookup, instantiation, and config injection. Any load/instantiate failure is logged and falls back to `DUOptimizedFactory`.

## State and Persistence Behavior

The interface itself has no state. Implementations define cache and refresh persistence behavior.

## Dependencies and Integration Points

It depends on HDDS config annotations and is a key integration point between datanode volume code and specific usage implementations.

## Risks and Test Signals

Because the default is `DUOptimizedFactory`, generic callers using only `paramsFor(File)` may receive `null`. Reflection failures are non-fatal and can silently select a different implementation except for logs. Tests should cover default fallback, invalid class names, custom class loading, and overload behavior.
