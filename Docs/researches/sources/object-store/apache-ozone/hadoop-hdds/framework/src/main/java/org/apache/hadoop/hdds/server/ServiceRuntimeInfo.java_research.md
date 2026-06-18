# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/ServiceRuntimeInfo.java

## Purpose

`ServiceRuntimeInfo` defines common runtime metadata exposed by Ozone service components without using an MXBean/MBean suffix that can confuse JMX property discovery.

## Important APIs, Types, and Functions

Methods are `getNamespace()` with default empty string, `getVersion()`, `getSoftwareVersion()`, and `getStartedTimeInMillis()`.

## Control Flow

There is no implementation flow beyond the default namespace. Service-specific MXBean interfaces extend this interface and implementations provide version/start-time values.

## State and Persistence Behavior

No state or persistence is defined.

## Dependencies and Integration Points

It integrates service implementations with JMX/runtime reporting and is implemented by `ServiceRuntimeInfoImpl`.

## Risks and Edge Cases

Implementations must call their start-time setter or return a meaningful value. Naming convention is part of the JMX behavior contract.

## Test Signals

Test concrete MXBean exposure, default namespace behavior, and start-time/version values from implementations.
