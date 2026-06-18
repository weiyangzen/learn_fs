# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ShardSizing.h

## Purpose
`ShardSizing.h` declares helpers for computing permitted shard size and I/O bounds used by data distribution split/merge decisions.

## Important APIs, Types, And Functions
`ShardSizeBounds` contains `StorageMetrics max`, `min`, and `permittedError`, equality comparison, and `shardSizeBoundsBeforeTrack`. Functions `getShardSizeBounds`, `getMaxShardSize`, and `ddLargeTeamEnabled` compute bounds from key ranges, database-size estimates, and feature knobs.

## Control Flow
DD asks for size bounds before or during shard tracking, compares live `StorageMetrics` to min/max/error windows, and uses the result to split large/hot shards or merge small/cold ones.

## State And Persistence Behavior
The file has no state. Computed values influence persistent data movement and shard-boundary mutations elsewhere.

## Dependencies And Integration Points
It depends on FDB types and `StorageMetrics`. It integrates with DD queueing, shard metrics, team sizing, and large-team behavior.

## Risks And Edge Cases
Incorrect bounds can cause excessive shard churn, oversized shards, or missed hot-shard splits. `ddLargeTeamEnabled` must reflect configuration consistently across DD actors.

## Test Signals
Tests should cover boundary formulas for small and large database estimates, before-track defaults, large-team enablement, and split/merge decisions around permitted error thresholds.
