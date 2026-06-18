# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/DiskBalancerProtocol.java

## Purpose

`DiskBalancerProtocol` defines the client-to-datanode administrative RPC contract for DiskBalancer operations.

## Important APIs, Types, and Functions

It exposes `getDiskBalancerInfo(GetDiskBalancerInfoRequestProto)`, a default no-arg `getDiskBalancerInfo()`, `startDiskBalancer(@Nullable DiskBalancerConfigurationProto)`, `stopDiskBalancer()`, and `updateDiskBalancerConfiguration(DiskBalancerConfigurationProto)`. Methods are annotated `@Idempotent`.

## Control Flow

The interface defines no implementation. The default info method constructs a current-client-version request and delegates to the request-taking method.

## State and Persistence Behavior

No local state. Implementations may persist DiskBalancer configuration or use the last persisted config when start receives null.

## Dependencies and Integration Points

PB client/server translators implement the wire layer, and datanode services implement the actual operations.

## Risks and Test Signals

The null config semantics for start must be preserved across translators. Tests should cover default request versioning, null start config, non-null update validation, and idempotent retry behavior at the RPC layer.
