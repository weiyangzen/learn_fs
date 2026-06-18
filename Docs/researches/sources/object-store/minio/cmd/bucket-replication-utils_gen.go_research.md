# sources/object-store/minio/cmd/bucket-replication-utils_gen.go

Purpose: Generated `tinylib/msgp` codecs for replication utility and resync/MRF structs declared in `bucket-replication-utils.go`.

Important APIs/types: Implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `BucketReplicationResyncStatus`, `MRFReplicateEntries`, `MRFReplicateEntry`, `ReplicateDecision`, `ReplicationState`, `ResyncDecision`, `ResyncStatusType`, `ResyncTarget`, `ResyncTargetDecision`, `ResyncTargetsInfo`, and `TargetReplicationResyncStatus`.

Control flow: Struct codecs read/write msgp maps with compact field tags where configured. Map-bearing types (`BucketReplicationResyncStatus.TargetsMap`, `MRFReplicateEntries.Entries`, decision maps, replication state maps) allocate or clear maps on decode before filling entries. Unknown fields are skipped. Enum-like `ResyncStatusType` is encoded as an integer. Nested resync target/status values delegate to their own generated methods.

State and persistence: This file is the binary compatibility layer for persisted resync metadata, MRF metadata, and internal replication state snapshots. Only exported/tagged fields are serialized. Unexported operational fields such as `MRFReplicateEntry.versionID`, `MRFReplicateEntry.sz`, and `TargetReplicationResyncStatus.Error` are intentionally excluded.

Dependencies and integration points: Depends on `github.com/tinylib/msgp/msgp` and the MinIO replication package for map values of `replication.StatusType`. Regenerated from `bucket-replication-utils.go` by the msgp generator.

Risks: Generated map encode order follows Go map iteration, so byte-for-byte deterministic output is not guaranteed for maps even though decoded values should be equivalent. Struct/tag changes require regeneration and test updates. Excluding unexported fields is important for privacy/runtime state, but code that expects version IDs or object sizes from decoded MRF entries will not get them. Manual edits are fragile and should be avoided.

Test signals: `bucket-replication-utils_gen_test.go` round-trips and benchmarks every generated type in this file. Behavioral correctness of the underlying decisions and composite status rules is covered separately by `bucket-replication-utils_test.go`.
