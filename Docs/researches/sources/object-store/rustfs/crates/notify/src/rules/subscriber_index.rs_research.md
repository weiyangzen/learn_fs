# sources/object-store/rustfs/crates/notify/src/rules/subscriber_index.rs

## Purpose
Provides a concurrent bucket-to-snapshot index for fast subscriber checks with atomic whole-snapshot replacement.

## Important APIs, types, and functions
- `SubscriberIndex` holds `ShardedHashMap<String, Arc<ArcSwap<BucketRulesSnapshot<DynRulesContainer>>>>` plus a cached empty rules container.
- `new` accepts the empty rules container.
- `load_snapshot` returns the current snapshot or an empty snapshot.
- `has_subscriber` checks the snapshot event mask.
- `store_snapshot` creates or updates an `ArcSwap` cell for a bucket.
- `clear_bucket` replaces an existing bucket cell with an empty snapshot.
- `Default` builds a minimal empty rules container.

## Control flow
Writers compile a complete snapshot first and call `store_snapshot`, which swaps it atomically. Readers call `load_snapshot` and then inspect mask bits without observing intermediate state.

## State and persistence behavior
All state is in-memory. `clear_bucket` leaves the bucket cell present but with an empty snapshot.

## Dependencies and integration points
Uses `arc_swap`, `starshard::ShardedHashMap`, `BucketRulesSnapshot`, `DynRulesContainer`, and `EventName`. Wrapped by `NotificationSystemSubscriberView`.

## Risks and edge cases
The default missing-bucket path allocates a new empty snapshot each read, though it reuses the empty rules container. Bucket cells are not removed on clear, so many created/cleared buckets may leave empty cells.

## Test signals
No direct tests in this file. Behavior is exercised through subscriber view and bucket config manager usage.
