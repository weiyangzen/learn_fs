<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerInspectorUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerInspectorUtil.java

## Purpose

`ContainerInspectorUtil` centralizes startup-time container inspector registration and execution by container type. It currently wires `KeyValueContainerMetadataInspector` for key-value containers. The complete 86-line file was read.

## Important APIs, Types, and Functions

The static `INSPECTORS` map is keyed by `ContainerProtos.ContainerType` and stores lists of `ContainerInspector`. Public static methods are `load()`, `unload()`, `isReadOnly(ContainerType)`, and `process(ContainerData, DatanodeStore)`.

## Control Flow

Static initialization creates an inspector list for every container type and adds the key-value metadata inspector to `KeyValueContainer`. `load` and `unload` iterate all inspectors. `isReadOnly` returns false if any inspector for that type is mutating. `process` dispatches a container and its store to each inspector registered for the container's type.

## State and Persistence Behavior

The utility owns only static inspector lists. Persistence effects depend on individual inspectors; the key-value metadata inspector may inspect or repair metadata depending on its own mode.

## Dependencies and Integration Points

It depends on `ContainerInspector`, `ContainerData`, `DatanodeStore`, protobuf container types, and `KeyValueContainerMetadataInspector`.

## Risks and Edge Cases

The map assumes every enum value is present from static initialization. Adding new container types without inspectors is safe but no-op. Inspector load/unload/process exceptions are not caught here and can propagate to startup paths.

## Test Signals

Tests should verify key-value inspector registration, read-only aggregation, process dispatch by type, load/unload invocation, and behavior with container types that have no inspectors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerInspectorUtil.java -->
