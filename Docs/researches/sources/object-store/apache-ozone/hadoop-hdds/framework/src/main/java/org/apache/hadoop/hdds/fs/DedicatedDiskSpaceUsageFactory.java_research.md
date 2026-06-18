# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DedicatedDiskSpaceUsageFactory.java

## Purpose

This factory builds fast df-style usage checks for dedicated datanode disks. It avoids cache persistence because filesystem capacity queries are cheap.

## Important APIs, Types, and Functions

`setConfiguration` loads `DedicatedDiskSpaceUsageFactory.Conf`. `paramsFor(File)` returns a `SpaceUsageCheckParams` with `DedicatedDiskSpaceUsage`, configured refresh period, and `SpaceUsagePersistence.None.INSTANCE`. Config key `hdds.datanode.df.refresh.period` defaults to five minutes.

## Control Flow

The factory reads refresh configuration once and produces independent params per volume.

## State and Persistence Behavior

No persistence is used for generated params. The factory stores the loaded config object.

## Dependencies and Integration Points

It implements `SpaceUsageCheckFactory` and can be selected by `hdds.datanode.du.factory.classname`.

## Risks and Test Signals

The factory assumes dedicated disks; using it on shared disks misattributes space. Tests should verify config binding, no-op persistence, and refresh period defaults.
