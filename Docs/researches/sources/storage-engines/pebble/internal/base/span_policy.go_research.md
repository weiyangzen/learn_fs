# sources/storage-engines/pebble/internal/base/span_policy.go

Purpose: Defines per-key-span policy hints for compression, value separation, blob storage, and warm/cold tiering.

APIs and types: `SpanPolicy`, `ValueStoragePolicyAdjustment`, `TieringAttribute`, `TieringSpanID`, `TieringPolicy`, and `TieringPolicyAndExtractor`.

Control flow and state: `SpanPolicy.IsDefault` detects whether any non-range policy is set. `StillCovers` checks whether a key remains within the policy end and asserts the key is not before start under invariants. String methods render human-readable policy descriptions. Value storage policy flags describe overrides to global separation heuristics. Tiering policy uses span ID plus age threshold and extractor metadata.

Persistence and dependencies: Span policies are runtime inputs but affect persistent placement of values into SSTables/blob files and tier metadata. Depends on key comparison, time durations, string helpers, and invariants.

Integration points: Flush, compaction, blob rewrite, and tiering decisions call policy providers to decide compression/value-storage/tier assignment. `KVMeta` in `internal.go` carries tiering metadata produced by these paths.

Risks: Tiering invariants are cross-layer and eventual-consistency tolerant but subtle; conflicting span IDs over overlapping key ranges can corrupt tiering assumptions. Policy string output must track added fields. Value-separation overrides interact with MVCC suffix heuristics.

Test signals: No direct tests in this subset; correctness depends on compaction/blob/tiering integration tests.
