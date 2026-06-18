# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ShardMetrics.h

## Purpose
This header defines lightweight data structures for tracking aggregate metrics of a shard while data distribution observes size, bandwidth, and usable-region state.

## Important APIs, Types, And Functions
`ShardMetrics` contains `StorageMetrics metrics`, `lastLowBandwidthStartTime`, and `shardCount`, with equality comparison and constructor. `ShardTrackedData` bundles futures for shard, byte, and usable-region tracking plus an `AsyncVar<Optional<ShardMetrics>>` stats handle.

## Control Flow
DD tracking actors update the futures and async stats value. Consumers read `stats` to decide split/merge/movement actions.

## State And Persistence Behavior
All state is in memory. `shardCount` records aggregation over smaller shards but is not durable.

## Dependencies And Integration Points
It depends on storage-server interfaces for `StorageMetrics` and Flow futures/async variables. It integrates with DD shard tracking, shard split/merge logic, and load balancing.

## Risks And Edge Cases
Equality compares double timestamps exactly, which is appropriate for state comparison but fragile for computed values. Cancelled tracking futures or absent stats can stall DD decisions.

## Test Signals
Tests should observe DD behavior under changing storage metrics, low-bandwidth timing, aggregation over multiple shards, and cancellation/cleanup of tracking actors.
