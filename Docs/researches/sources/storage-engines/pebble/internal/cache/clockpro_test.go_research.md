# sources/storage-engines/pebble/internal/cache/clockpro_test.go

## Purpose
This file tests one targeted CLOCK-Pro reservation regression: `Reserve` must clamp `coldTarget` when effective capacity shrinks, otherwise eviction can over-drain the cache.

## Important APIs, Types, And Functions
`TestReserveColdTarget` creates a one-shard cache, many handles, inserts one-byte values through `setTestValue`, calls `Cache.Reserve`, and checks `Cache.Size`.

## Control Flow
The test inserts 50 one-byte entries into a 100-byte cache, verifies size 50, reserves 51 bytes, and expects eviction down to 48 bytes rather than an empty cache. The scenario depends on shard-level CLOCK-Pro size/target logic.

## State And Persistence Behavior
Only in-memory cache state is affected. Handles are closed and the cache is unreferenced with defers.

## Dependencies And Integration Points
It uses the helper from `cache_test.go`, `NewWithShards`, `Handle`, and `require`. It specifically validates `shard.Reserve`, `targetSize`, `evict`, and `coldTarget` adjustment in `clockpro.go`.

## Risks And Edge Cases
The test protects an off-by-one/over-eviction path when reservation makes target capacity smaller than the previous `coldTarget`. It does not validate multi-shard distribution or release behavior, which are covered in `cache_test.go`.

## Test Signals
The signal is exact cache size before and after reservation. A result of zero would identify the historical bug called out in the comments.
