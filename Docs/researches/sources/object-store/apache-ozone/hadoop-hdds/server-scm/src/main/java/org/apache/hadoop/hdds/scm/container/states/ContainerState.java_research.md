<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerState.java

## Purpose

`ContainerState` is a value object representing a container selection key composed of owner and pipeline ID.

## Important APIs, Types, and Functions

It exposes `getOwner`, `equals`, `hashCode`, and `toString`. Fields are immutable `owner` and `PipelineID`.

## Control Flow

There is no complex flow. Equality checks class and compares owner plus pipeline ID using Apache commons builders; hash code uses the same fields.

## State and Persistence Behavior

State is immutable and in-memory. The class does not persist data.

## Dependencies and Integration Points

It depends on `PipelineID` and is intended for container state/key maps where owner and pipeline distinguish allocation pools.

## Risks and Edge Cases

`toString` labels the object as `ContainerKey`, which may be legacy naming. Null owner or pipeline is not rejected in the constructor, so equality and hash code must tolerate nulls through the builder implementation.

## Test Signals

Tests should assert equality/hash-code for same and different owner/pipeline pairs, null-field behavior if allowed, and stable string format if logs depend on it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerState.java -->
