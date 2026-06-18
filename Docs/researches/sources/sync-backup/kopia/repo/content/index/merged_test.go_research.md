# sources/sync-backup/kopia/repo/content/index/merged_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/merged_test.go_research.md`.

Purpose: validates merged-index lookup, sorted iteration, range filtering, error propagation, close handling, and duplicate-resolution rules.

Important coverage: `TestMerged` builds three v2 indexes with overlapping and unique IDs, checks `ApproximateCount`, verifies `GetInfo` picks the newest timestamp, ensures non-deleted wins over deleted at equal timestamps, confirms callback errors propagate, checks empty merged iteration, and tests several `IDRange` values. `TestMergedGetInfoError` verifies shard lookup errors are wrapped and returned. `TestMergedIndexIsConsistent` permutes shard order to prove deterministic tie breaking by timestamp, deleted flag, and highest pack blob ID.

Control flow and fixtures: helper `indexWithItems` builds a `Builder`, serializes v2 bytes, and opens an index. `iterateIDRange` collects IDs in emitted order.

State and persistence behavior: tests focus on read-only merged views, not blob storage. They encode the conflict-resolution policy used by committed content indexes.

Dependencies: `testify/require`, pack index builder/open functions, and blob IDs.

Risks and gaps: tests do not force slow shard goroutines or close errors from custom indexes, but they strongly cover ordering and duplicate semantics that affect deletion and concurrent writer visibility.
