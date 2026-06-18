# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DUFactory.java

## Purpose

`DUFactory` creates `SpaceUsageCheckParams` backed by the shell-based `DU` implementation and a cache file. It is the classic accurate disk-usage factory for datanode volumes.

## Important APIs, Types, and Functions

`setConfiguration(ConfigurationSource)` loads `DUFactory.Conf`. `paramsFor(File)` creates a `DU`, reads the refresh period, and uses `SaveSpaceUsageToFile(new File(dir, "scmUsed"), refreshPeriod)`. `Conf` binds `hdds.datanode.du.refresh.period`, defaulting to one hour.

## Control Flow

Factory creation is configuration-driven. Each requested directory receives an independent source, refresh period, and persistence object.

## State and Persistence Behavior

The factory stores loaded configuration. Resulting params persist used-space cache in `scmUsed` under the volume directory.

## Dependencies and Integration Points

It implements `SpaceUsageCheckFactory` and is available through factory class-name configuration, although the current default factory is `DUOptimizedFactory`.

## Risks and Test Signals

If `setConfiguration` is not called, `conf` is null. Cache file creation depends on a positive refresh period because `SaveSpaceUsageToFile` rejects zero. Tests should verify config binding, cache path, and params construction.
