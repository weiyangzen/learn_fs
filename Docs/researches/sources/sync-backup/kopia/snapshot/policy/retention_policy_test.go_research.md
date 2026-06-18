# sources/sync-backup/kopia/snapshot/policy/retention_policy_test.go

Purpose: table-driven coverage for retention reason assignment and compact display helpers.

Important APIs/types/functions: `TestRetentionPolicyTest`, `TestCompactPins`, and `TestCompactRetentionReasons`. The tests create `snapshot.Manifest` instances with RFC3339 timestamps, optional `IncompleteReason`, and expected retention tags.

Control flow: each retention case builds a full manifest set and a filtered retained-only set, calls `ComputeRetentionReasons` on both, and compares the resulting tags with `cmp.Diff`. Helper tests verify pin dedupe/sort and RLE-style reason compaction.

State and persistence: no repository state is used; the tests mutate manifest slices in memory. `Description` stores the original timestamp key to map results back to expectations.

Dependencies and integration points: exercises the same `RetentionPolicy` behavior consumed by snapshot expiration and UI output.

Risks and test signals: expectations encode exact cutoff semantics around missing months, week numbers, and incomplete minimum count. Failures show as tag diffs for specific timestamps.
