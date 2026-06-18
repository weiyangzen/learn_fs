# sources/storage-engines/foundationdb/fdbserver/core/ShardSizing.cpp

## sources/storage-engines/foundationdb/fdbserver/core/ShardSizing.cpp

Purpose: computes data distribution shard size bounds and feature gates for large teams. It converts database size estimates and key-range context into `ShardSizeBounds` consumed by data distribution and shard splitting/merging logic.

Important APIs: `ShardSizeBounds::shardSizeBoundsBeforeTrack`, `getShardSizeBounds`, `getMaxShardSize`, and `ddLargeTeamEnabled`.

Control flow and state: `shardSizeBoundsBeforeTrack` returns sentinel bounds where byte fields are `-1` and non-byte maxima/permitted errors are infinity, representing pre-tracking behavior. `getShardSizeBounds` gives system keyspace shards under `keyServersKeys` a separate `KEY_SERVER_SHARD_BYTES` maximum, otherwise uses the supplied maximum. The first shard beginning at `allKeys.begin` may shrink to zero bytes, while other shards use `maxShardSize / SHARD_BYTES_RATIO` as the minimum. `getMaxShardSize` scales from `MIN_SHARD_BYTES + sqrt(dbSizeEstimate) * SHARD_BYTES_PER_SQRT_BYTES`, multiplies by `SHARD_BYTES_RATIO`, caps at `MAX_SHARD_BYTES`, optionally raises to `MAX_LARGE_SHARD_BYTES`, and traces the result with suppression.

Dependencies and integration: depends on `SystemData` key ranges, `StorageMetrics`, and `SERVER_KNOBS`. Data distribution uses these bounds when deciding whether shards are too large, too small, or eligible for large-team handling.

Risks and tests: size math directly impacts movement volume and shard churn. Negative/sentinel byte fields are meaningful and should not be treated as real sizes. Large-team enablement is disabled when location metadata encoding is active, so tests should cover both metadata modes, system key ranges, zero database estimates, and large-shard knob combinations.
