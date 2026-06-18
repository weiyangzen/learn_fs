# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/DatanodeConfiguration.java

## Purpose
`DatanodeConfiguration` is the annotated HDDS datanode configuration bean for container-service runtime behavior. It centralizes limits and tunables for command queues, close/delete executors, block deletion, volume health checks, disk free-space thresholds, RocksDB schema/logging/compaction behavior, read-thread sizing, and gRPC backlog.

## Important APIs and Types
The class extends `ReconfigurableConfig` and is annotated with `@ConfigGroup(prefix = "hdds.datanode")`. Public getters and setters expose values used by `DatanodeStateMachine`, command handlers, volume checks, RocksDB helpers, and container IO paths. Notable APIs include `validate()`, `getMinFreeSpace(capacity)`, `getHardLimitMinFreeSpace(capacity)`, `getSoftBandMinFreeSpaceWidth(capacity)`, `getCommandQueueLimit()`, `getBlockDeleteThreads()`, `getBlockDeleteQueueLimit()`, `getDeleteContainerTimeoutMs()`, and schema/RocksDB accessors.

## Control Flow
The configuration framework populates fields from `@Config` annotations and invokes `@PostConstruct validate()`. Validation normalizes invalid values, logs warnings, and calls `validateMinFreeSpace()` to enforce ratio bounds and keep the hard-limit ratio no greater than the soft/reporting ratio.

## State and Persistence Behavior
This file is in-memory configuration state only, but its values control persistent side effects elsewhere: datanode ID writes, container metadata updates, RocksDB delete-transaction tables, and volume failure policy. Free-space thresholds feed storage reports and local write rejection; block deletion values determine retry and locking pressure.

## Dependencies and Integration Points
It depends on HDDS config annotations, `StorageSize`, `DurationFormatUtils`, and `ReconfigurableConfig`. `DatanodeStateMachine` consumes it when constructing command executors and the replication supervisor. `DeleteBlocksCommandHandler`, `DeleteContainerCommandHandler`, disk-check services, RocksDB options, and volume selection use its values.

## Risks
Misconfigured queue sizes and thread counts can either drop commands or overrun datanode resources. Disk-check sliding windows are sensitive: if shorter than the periodic interval, sparse failures may be missed. Free-space hard-limit and soft-limit ratios affect write availability and SCM capacity planning. One setter is named `getVolumeHealthCheckFileSize(int)` despite mutating state, which is easy to misuse.

## Test Signals
Test coverage should verify `validate()` fallback behavior, ratio clamping, free-space calculations, disk-check window guards, executor/queue values, and reconfigurable block deletion limit behavior. Existing `@VisibleForTesting` methods indicate expected unit checks around soft-band width and hard-limit ratio.
