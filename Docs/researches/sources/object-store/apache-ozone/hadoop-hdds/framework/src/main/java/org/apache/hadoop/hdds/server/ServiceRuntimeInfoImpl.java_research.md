# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/ServiceRuntimeInfoImpl.java

## Purpose

`ServiceRuntimeInfoImpl` is a base implementation of `ServiceRuntimeInfo` that reports Hadoop/Ozone version strings and service start time.

## Important APIs, Types, and Functions

The constructor accepts `VersionInfo`. `getVersion()` returns version plus revision, `getSoftwareVersion()` returns version only, `getStartedTimeInMillis()` returns the stored start time, and `setStartTime()` sets it to `System.currentTimeMillis()`.

## Control Flow

Services instantiate with version info and call `setStartTime` during startup. JMX/runtime queries read the stored values.

## State and Persistence Behavior

It stores in-memory start time and immutable version info. No persistence.

## Dependencies and Integration Points

It depends on `org.apache.hadoop.hdds.utils.VersionInfo` and is intended as a superclass for service runtime/JMX implementations.

## Risks and Edge Cases

If `setStartTime` is never called, start time remains zero. The constructor is protected, so only subclasses can instantiate it.

## Test Signals

Test formatted version string, software version string, start time initially zero, and start time update within expected wall-clock range.
