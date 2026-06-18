# sources/object-store/minio/cmd/bucket-replication-utils_gen_test.go

Purpose: Generated msgp tests and benchmarks for replication utility serialization, including resync metadata, MRF entries, replication decisions, and replication state.

Important APIs/tests: For `BucketReplicationResyncStatus`, `MRFReplicateEntries`, `MRFReplicateEntry`, `ReplicateDecision`, `ReplicationState`, `ResyncDecision`, `ResyncTarget`, `ResyncTargetDecision`, `ResyncTargetsInfo`, and `TargetReplicationResyncStatus`, the file defines marshal/unmarshal tests, encode/decode tests, and benchmarks. It also benchmarks append-style marshaling.

Control flow: Tests use the standard msgp generated pattern: marshal a zero-value value, unmarshal into a new value, assert no trailing bytes, verify `msgp.Skip`, then repeat through streaming encode/decode. Benchmarks repeatedly execute each codec path after resetting timers.

State and persistence: Tests do not create persistent files. They validate the generated binary contract mechanically, but mostly with zero-value instances rather than populated resync maps or MRF entries.

Dependencies and integration points: Uses `testing`, `bytes`, and `github.com/tinylib/msgp/msgp`. It protects the generated codec file from compile-time and basic runtime regressions after msgp regeneration.

Risks: Zero-value round trips do not validate non-empty maps, timestamp values, enum variants, or excluded fields. Generated benchmarks do not enforce performance budgets. The file should be regenerated, not hand-edited.

Test signals: Provides broad serialization smoke coverage for `bucket-replication-utils_gen.go`; it should be paired with hand-written tests for metadata semantics, resync workflows, and MRF retry behavior.
