# sources/storage-engines/tikv/components/raftstore/src/store/worker/region.rs

Purpose: this raftstore worker handles region-local background jobs that must not run on the hot raft peer path: applying received snapshots, destroying stale data ranges, and asynchronously clearing peer metadata. It is a bridge between peer storage state, snapshot files, RocksDB range deletion/ingestion, coprocessor snapshot hooks, and raftstore routing callbacks.

Important APIs and types:
- `Task` has `Apply`, `Destroy`, and `ClearPeerMeta`. `Apply` carries a region id, peer id, atomic job status, and enqueue time. `Destroy` carries an encoded data range. `ClearPeerMeta` carries peer/region raft state plus merge/replication context and a lock over pending peer creation.
- `PendingDeleteRanges` is a `BTreeMap<start_key, StalePeerInfo>` that tracks logically destroyed ranges until old engine snapshots have drained. It exposes overlap draining, stale iteration by oldest snapshot sequence, and removal by start key.
- `Runner<EK, ER, R>` owns engine handles, `StoreMeta`, `SnapManager`, `CoprocessorHost`, router, pending apply queue, and pending delete ranges. It implements both `Runnable` and `RunnableWithTimer`.

Control flow:
- `run(Task::Apply)` optionally calls `pre_apply_snapshot`, appends the task to `pending_applies`, updates snap manager pending count, and calls `handle_pending_applies(false)`.
- `handle_pending_applies` preserves apply order and only runs when ingestion is unlikely to cause write stall and `KvEngine::can_apply_snapshot` accepts the current batch. Delayed tasks are retried from the timer path.
- `apply_snap` reads `RegionLocalState` and `RaftApplyState` from `CF_RAFT`, cleans overlapping data, registers the snapshot as applying, applies snapshot SSTs through `Snapshot::apply`, invokes coprocessor post hooks, writes the region state back as `PeerState::Normal`, deletes snapshot raft state, and synchronously commits the metadata update.
- `run(Task::Destroy)` inserts a delayed pending range and attempts stale cleanup. `clean_stale_ranges` deletes files first for ranges older than the oldest engine snapshot sequence, then deletes all keys and blobs, and finally removes pending range entries.
- `run(Task::ClearPeerMeta)` delegates to `clear_meta_in_kv_and_raft`; on success it sends `SignificantMsg::ReadyToDestroyPeer`, and on error it panics to avoid unsafe recreation/deletion races.

State and persistence behavior:
- Snapshot apply persistence is in `CF_RAFT`: region state and snapshot raft state are updated with `WriteOptions::sync(true)`, making the transition to normal durable before notifying peers.
- Snapshot data application mutates user CFs through snapshot ingestion/deletion strategies. Overlapping pending delete ranges are merged into the cleanup range before applying a new snapshot, protecting against stale range deletion after new data is installed.
- Delayed deletion state is only in-memory. It is an optimization and safety delay, not durable metadata; actual region/peer metadata destruction is persisted by `clear_meta_in_kv_and_raft`.
- Physical deletion uses multiple strategies: `DeleteFiles` for stale SST/blob cleanup when safe by snapshot sequence, `DeleteByRange` when configured, `DeleteByKey` for lock CF or forced cleanup, and writer/ingestion cleanup as a fallback.

Dependencies and integration points:
- Depends on `engine_traits` for KV/raft engines, write batches, range deletion, sequence numbers, and write-stall checks.
- Integrates with `SnapManager` for snapshot lifecycle registration/deregistration and temp ingest paths.
- Uses `CoprocessorHost` hooks around snapshot application: pre, post, committed, and cancel paths.
- Routes completion through `RaftStoreRouter`: `CasualMessage::SnapshotApplied` for apply results and `SignificantMsg::ReadyToDestroyPeer` for metadata clear completion.
- Scheduled by peer storage and store workers via the re-exported `RegionTask`/`RegionRunner`.

Risks and edge cases:
- Range deletion ordering is critical: overlap cleanup must precede snapshot application or stale delayed deletion could remove newly applied data.
- Several error paths intentionally panic or unwrap, especially durable apply metadata writes and peer metadata cleanup failures, because continuing can resurrect peers or corrupt overlapping regions.
- `PendingDeleteRanges::insert` panics if overlap remains; callers must drain overlaps first.
- Ingestion pressure can starve snapshot apply until compaction reduces L0 files; timer retry and metrics are the visibility mechanism.
- Delayed delete ranges are in memory, so process restart relies on durable peer metadata/region states rather than this optimization state.

Test signals:
- `test_pending_delete_ranges` covers overlap draining, stale iteration, insertion, and removal ordering.
- `test_stale_peer` validates delayed destruction waits for old snapshots and then deletes stale keys without deleting the end bound.
- `test_pending_applies` exercises write-stall deferral, snapshot generation/apply integration, coprocessor pre/post hooks, pending queue order, destroy delay behind apply pressure, and failpoint-controlled delayed apply.
