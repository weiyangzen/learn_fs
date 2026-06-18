# sources/storage-engines/tikv/components/backup-stream/src/metadata/checkpoint_cache.rs

## Purpose
`checkpoint_cache.rs` provides a short-lived per-task cache for global checkpoints used by `MetadataClient::get_region_checkpoint` to avoid repeatedly scanning metadata when many region checkpoint lookups happen close together.

## Important APIs, types, and functions
- `CheckpointCache` stores `last_access`, the cached `checkpoint`, and `cache_lease_time`.
- `Default` sets the checkpoint to zero and the lease to 12 seconds, matching the coordinator tick interval noted in the comment.
- `update` records the current coarse time and monotonically raises the cached checkpoint with `max`.
- `get` returns `None` when the cached checkpoint is zero or the lease expired; otherwise it returns the cached `TimeStamp`.

## Control flow
The client creates caches through `DashMap::entry(...).or_default()`. Reads call `get`; misses fall back to metadata queries and then call `update`.

## State and persistence behavior
State is process-local only. It is intentionally lease-based and monotonic to avoid moving cached checkpoint values backward. Durable checkpoint data remains in metadata storage.

## Dependencies and integration points
It depends on TiKV coarse `Instant` and `txn_types::TimeStamp`. It is not public from `metadata::mod`, but is used internally by `MetadataClient`.

## Risks and edge cases
- A cached global checkpoint can hide newer metadata for up to the lease duration, trading freshness for reduced metadata load.
- Because updates use `max`, a caller cannot lower the cached value before expiry.
- The default zero checkpoint is treated as no cache entry.

## Test signals
`test_basic` uses a 100 ms lease to verify empty cache behavior, monotonic update from 42 over 41, and expiration after sleep.
