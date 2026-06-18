# sources/object-store/minio/cmd/bucket-replication_test.go

## Purpose
This test file validates the decision logic for replication resync, especially existing-object replication and reset behavior. It focuses on pure state transitions in `replicationConfig.Resync` and the lower-level `replicationConfig.resync` wrapper rather than performing live object-layer or remote-target replication.

## Important APIs, types, and functions
The file defines a baseline `configs` slice containing one enabled replication rule with delete marker replication, delete replication, existing object replication, and replica modifications enabled. `replicationConfigTests` feeds `TestReplicationResync`, which calls `replicationConfig.Resync(ctx, info, dsc, tgtStatuses)`. `replicationConfigTests2` feeds `TestReplicationResyncwrapper`, which calls `replicationConfig.resync(info, dsc, tgtStatuses)` directly with explicit remote target metadata. Fixtures use production types such as `ObjectInfo`, `replicationConfig`, `ReplicateDecision`, `replicateTargetDecision`, `madmin.BucketTargets`, and replication status constants.

## Control flow
`TestReplicationResync` loops over high-level cases where config may be nil, existing object replication may be enabled, versioning may be absent/suspended, and object replication status may be completed. It checks `ResyncDecision.mustResync()`. `TestReplicationResyncwrapper` exercises target overlay cases for pending, failed, unset, and completed replication statuses; reset-in-progress with old reset metadata; reset ID changes; reset completion; and object `ModTime` relative to `ResetBeforeDate`.

## State and persistence behavior
The tests are table-driven and in-memory. They do not persist resync metadata or create MRF files. Persisted state is modeled through `ObjectInfo.UserDefined[xhttp.MinIOReplicationResetStatus]`, `ReplicationStatusInternal`, and remote target `ResetID`/`ResetBeforeDate`.

## Dependencies and integration points
The tests depend on replication rule structures, `UTCNow`, `nullVersionID`, `xhttp.MinIOReplicationResetStatus`, and `madmin.BucketTargets`. They represent the metadata shapes produced by bucket replication and admin target configuration.

## Risks and test signals
Coverage is narrow but important: pending/failed/unset statuses and changed reset IDs produce `mustResync == true`, while completed objects without an active/new reset do not. Gaps include multi-target mixed states, actual object metadata mutation, queue behavior, MRF persistence, delete replication execution, proxying, and multipart replication. Some cases use current time offsets rather than fixed timestamps.
