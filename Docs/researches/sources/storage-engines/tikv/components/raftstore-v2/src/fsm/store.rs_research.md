# sources/storage-engines/tikv/components/raftstore-v2/src/fsm/store.rs

Purpose: Implements store-wide FSM state and metadata for raftstore-v2, including read delegates, region range lookup, store ticks, and dispatch for control-plane `StoreMsg`s.

Important APIs/types/functions: `StoreMeta<EK>` tracks `store_id`, read delegates, read progress registry, range index `(region_end_key, epoch.version) -> region_id`, and region initialization state. `set_region` and `remove_region` maintain range metadata with corruption assertions. `StoreRegionMeta` impl exposes store id, read progress, `search_region`, and reader lookup. `Store` tracks store id, last compact checked key, start time, and logger. `StoreFsm` owns `Store` plus a receiver. `StoreFsmDelegate` handles start, tick scheduling, tick dispatch, and message dispatch.

Control flow: On start, the delegate records Unix start time, sends a PD store heartbeat, and schedules cleanup/import-SST and snapshot-GC ticks. `schedule_tick` creates timer futures that force-send `StoreMsg::Tick`. `handle_msgs` dispatches start, ticks, raft messages for unknown peers, split init, store unreachable, merge commit requests, test wait flush, latency inspect, and unsafe recovery store operations.

State and persistence behavior: `StoreMeta` is in-memory authoritative metadata shared behind a mutex. It mirrors persisted region states loaded from raft engine and updated by peer/apply results. Store ticks schedule background actions; actual persistence is delegated to store/peer operation methods and raft engine writes.

Dependencies and integration points: It uses `batch_system::Fsm`, raftstore read progress and store-region traits, TiKV timer helpers, `keys::data_key/data_end_key`, `StoreContext`, and router `StoreMsg`/`StoreTick`. `StorePoller` drives this FSM as the control FSM.

Risks: Region range invariants are protected with asserts and panics, so corrupt metadata can crash the process. Overlapping v2 ranges are handled by including epoch version in the range key; lookup code must consider initialized state and key ordering carefully. Timer tasks are detached through `poll_future_notify`, so send failures are only logged.

Test signals: No local unit tests. Integration should cover region metadata updates/removal, range search with overlapping versions, start idempotency panic, store tick rescheduling, and unknown-peer raft message handling.
