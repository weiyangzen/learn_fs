# sources/storage-engines/tikv/components/raftstore/src/coprocessor/region_info_accessor.rs

## Purpose
`region_info_accessor.rs` maintains a worker-backed, in-memory index of region metadata, roles, bucket counts, leader ids, and recent heartbeat activity. It lets other components query region coverage and high-activity regions without directly walking raftstore internals.

## Important APIs, Types, And Functions
`RaftStoreEvent` models create, update, destroy, role-change, bucket-update, and activity-update events. `RegionInfo` stores `Region`, `StateRole`, and bucket count. `RangeKey` normalizes finite keys and empty end-key infinity so region ranges can be ordered in a `BTreeMap`.

`RegionInfoQuery` is the worker task enum for raftstore events and queries. `RegionEventListener` implements `RegionChangeObserver`, `RoleObserver`, and `RegionHeartbeatObserver`, forwarding events to the worker scheduler. `RegionCollector` owns the maps: `regions`, `region_ranges`, `region_activity`, and shared `region_leaders`. `RegionInfoAccessor` owns the worker and implements `RegionInfoProvider`.

Key methods include `check_region_range`, `handle_raftstore_event`, `handle_seek_region`, `handle_get_regions_in_range`, `handle_get_top_regions`, and provider methods such as `find_region_by_key`, `get_top_regions`, and `get_regions_stat`.

## Control Flow
`RegionInfoAccessor::new` starts a dedicated timed worker and registers `RegionEventListener` at priority 1. Raftstore observer hooks enqueue `RegionInfoQuery::RaftStoreEvent`. The collector first rejects invalid epoch-version-zero events and uninitialized role changes, then checks whether the incoming region is stale compared with same-id or overlapping regions. Non-stale events update the hash map and end-key index, possibly clearing older overlapping entries.

Queries are also scheduler messages. Async callbacks are used for seek and find-by-id; synchronous provider methods build an mpsc channel, schedule a query, and block waiting for the callback response. Timer ticks refresh region, leader, and bucket-count gauges every 10 seconds.

## State And Persistence Behavior
All collected state is in memory and intentionally approximate. It can lag raftstore and may temporarily omit regions during split/merge. `region_leaders` is shared through `Arc<RwLock<HashSet<u64>>>` for direct consumers. Destroy removes region metadata, end-key mapping, activity, and leader membership. No durable persistence is performed; restart reconstructs state from future raftstore events.

## Dependencies And Integration Points
Depends on `engine_traits::KvEngine`, `kvproto::metapb::Region`, `pd_client::RegionStat`, raft roles, TiKV worker utilities, and coprocessor observer traits. It feeds in-memory engine/cache decisions through `get_top_regions`, raft KV through leader-id access, and Prometheus metrics via `REGION_COUNT_GAUGE_VEC`.

## Risks
Range correctness depends on `RangeKey` and epoch comparisons. Event reordering around split/merge is expected; stale filtering handles many cases but comments acknowledge rare role inaccuracies. Provider methods that block on mpsc receive can fail if the worker stops. `handle_get_regions_stat` unwraps `self.regions.get(&id)`, assuming activity cannot outlive region metadata. Top-region selection is `O(N log N)` over heartbeat activity and logs debug summaries, so large deployments must keep heartbeat volume bounded.

## Test Signals
Tests cover `RangeKey` ordering, invalid-version filtering, epoch staleness, clearing overlapped regions, basic create/update/destroy/role behavior, split and merge event order permutations, extreme split/merge races, mock provider range/seek behavior, and top-region filtering by leadership, flashback, iterated count, and MVCC amplification.
