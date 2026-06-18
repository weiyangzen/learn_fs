# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerInfo.java

## Purpose
Primary SCM metadata model for a container. It tracks ID, lifecycle state and transition time, previous state for rollback, pipeline, replication config, size/key counters, owner, delete transaction ID, sequence ID, health state, and suppression flag.

## Important APIs, Types, And Functions
Important APIs include `fromProtobuf`, `getProtobuf`, `getCodec`, state getters/setters, `revertState`, `isOpen`, `isDeleted`, update methods for delete transaction/sequence IDs, JSON-facing getters, and nested `Builder`. The DB codec delegates to `ContainerInfoProto`.

## Control Flow
Builders construct instances from runtime allocation or protobuf. `setState` snapshots previous state and uses the configured clock for state-enter time; `revertState` restores the prior state once. `getProtobuf` serializes replication config as EC or legacy factor and includes optional pipeline/suppressed fields.

## State And Persistence
Container metadata is mutable in memory. `usedBytes` is volatile; other fields require external synchronization. The protobuf codec persists the metadata in SCM DBs. `previousState` is transient and JSON-ignored.

## Dependencies And Integration Points
Depends on Jackson annotations, HDDS replication configs, `PipelineID`, `ContainerID`, DB codecs, and HddsProtos. Integrated by container manager, replication manager, Recon/API JSON, and block deletion.

## Risks And Test Signals
Equality ignores many fields, sequence updates rely on assertions, and health state is not serialized in this protobuf path. Tests should cover protobuf/codec round trips, state transition/revert, EC versus RATIS serialization, suppressed JSON behavior, and concurrent used-byte updates.
