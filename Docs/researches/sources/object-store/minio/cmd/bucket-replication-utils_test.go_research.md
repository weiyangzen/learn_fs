# sources/object-store/minio/cmd/bucket-replication-utils_test.go

Purpose: Hand-written unit tests for central replication utility semantics: per-target result aggregation, decision string parsing, and composite replication status.

Important APIs/tests: `TestReplicatedInfos` exercises `replicatedInfos.CompletedSize`, `ReplicationStatusInternal`, `ReplicationStatus`, and `Action`. `TestParseReplicateDecision` exercises string round-tripping through `ReplicateDecision.String` and `parseReplicateDecision`. `TestCompositeReplicationStatus` exercises `ReplicationState.CompositeReplicationStatus`.

Control flow: Table-driven fixtures cover empty target lists, completed single-target replication, mixed completed/failed targets, pending/failed targets, empty decision strings, one and multiple target decisions, and composite states with missing metadata, valid per-target pending/failed/completed strings, malformed status strings, and backward-compatible `REPLICA` status.

State and persistence: The tests are pure in-memory and do not interact with bucket metadata, object layers, or resync files. They construct helper structs directly.

Dependencies and integration points: Uses Go `testing` and MinIO replication enum constants. These tests guard behavior consumed by replication workers, stats updates, object metadata updates, and handlers that report composite state.

Risks: `TestParseReplicateDecision` parses `test.expDsc.String()` rather than the raw `test.dsc`, so the invalid-format fixture does not actually exercise invalid input. The tests do not cover version purge status composition, reset status maps, `getReplicationState`, `getHealReplicateObjectInfo`, content-range parsing, or MRF conversion. Map string order from `ReplicateDecision.String` can be nondeterministic for multi-target maps, though the test compares parsed maps rather than raw strings.

Test signals: Strong signal for the most important status aggregation rules: failures dominate, all targets completed yields completed, empty state yields empty, and newly completed targets contribute size. It also documents expected backward compatibility for single-string replica status.
