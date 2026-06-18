# sources/storage-engines/tikv/components/raftstore/src/store/worker/read.rs

## Purpose
This file implements raftstore's local read fast path. It lets eligible read-only raft commands bypass the raft proposal path when local metadata proves the read is safe: leader lease reads, stale reads guarded by safe timestamps, and follower-read-cache reads. It maintains cached `ReadDelegate`s derived from raftstore peer state, validates request headers and region state, manages snapshot reuse for batched reads, executes read commands against the KV engine snapshot, and redirects unsafe or unsupported requests back to raftstore.

## Important APIs, Types, and Functions
`ReadExecutor` abstracts execution over a tablet/KV engine. It provides `get_tablet()`, `get_snapshot()`, `get_value()`, and `execute()`. `execute()` handles `Get`, `Snap`, and `ReadIndex` commands and returns `ReadResponse`, including `RegionSnapshot` and coprocessor snapshot observation when `ReadContext.read_ts` is present.

`CachedReadDelegate<E>` wraps an `Arc<ReadDelegate>` with the KV engine clone needed to obtain snapshots. It implements `Deref<Target = ReadDelegate>`, `Clone`, and `ReadExecutor`.

`LocalReadContext<'a, E>` and `SnapCache<E>` control snapshot reuse. A `ThreadReadId` lets multiple commands from the same RPC batch share one engine snapshot if the cached read ID matches and the delegate has not changed since the read ID was created. Stale reads pass `None` and use a per-request snapshot instead.

`ReadExecutorProvider` abstracts access to source delegates. `StoreMetaDelegate<E>` implements it by locking `StoreMeta`, reading `store_id`, cloning `StoreMeta.readers[region_id]`, and returning the current reader-map length for LRU sizing.

`TrackVer` is the version invalidation primitive. Source delegates stored in `StoreMeta` have `source=true` and increment a shared atomic on updates/drop/pending-remove; cloned local delegates record the version at clone time and use `any_new()` to detect staleness.

`ReadDelegate` is the read-only peer view: region, peer id, term, applied term, optional remote leader lease, `last_valid_ts`, tag, bucket metadata, transaction extra-op state, transaction extension, `RegionReadProgress`, pending-remove flag, wait-data flag, and `TrackVer`. Key methods include `from_peer()`, `new()`, `update(Progress)`, `mark_pending_remove()`, `is_in_leader_lease()`, `maybe_renew_lease_advance()`, and `check_stale_read_safe()`.

`Progress` enumerates delegate updates: region, term, applied term, leader lease set/unset, region bucket metadata, and wait-data state.

`LocalReaderCore<D, S>` owns per-thread cached delegates in an LRU and validates request metadata. `LocalReader<E, C>` is the main fast-path reader with `propose_raft_command()`, `pre_propose_raft_command()`, `try_local_leader_read()`, `try_local_stale_read()`, `try_local_follower_read()`, `redirect()`, `read()`, and `release_snapshot_cache()`.

`Inspector` implements `RequestInspector` over a `ReadDelegate`, requiring `applied_term == term` and deferring exact lease timestamp validation until after snapshot acquisition.

## Control Flow
A caller enters through `LocalReader::read()` or `propose_raft_command()`. The reader increments local-read metrics, calls `pre_propose_raft_command()`, and either receives a delegate plus request policy, receives `None` and redirects to raftstore, or receives an error and completes the callback with an error response.

`LocalReaderCore::validate_request()` lazily caches store ID, checks store ID, loads or refreshes the region delegate from `StoreMeta`, rejects missing or pending-remove delegates, checks peer ID, term, region epoch, witness status, wait-data state, and flashback constraints. Stale epoch returns `Ok(None)` so raftstore can handle the request with fresher metadata.

`pre_propose_raft_command()` runs `Inspector::inspect()` and accepts local policies `ReadLocal`, `StaleRead`, `ReadIndexReplicaRead`, and `ReadIndex`. Other policies fall back to raftstore. `ReadIndex` is explicitly redirected because it still needs raft consensus.

For `ReadLocal`, `try_local_leader_read()` creates a `LocalReadContext`, obtains/reuses a snapshot before checking the lease, validates the snapshot timestamp against the remote leader lease, executes the read, attaches bucket metadata, and may send `CasualMessage::RenewLease` if the lease is near expiration. If the lease is invalid, the original command is redirected.

For `StaleRead`, `try_local_stale_read()` decodes the read timestamp from header flag data, checks `RegionReadProgress.safe_ts()` or `read_index_safe_ts()`, obtains a per-request snapshot, executes the read, attaches bucket metadata, then checks stale-read safety again to catch a race where safe ts regressed or became insufficient around snapshot creation. If a stale read is not safe and the same local peer is currently a valid leader, the code clears the stale-read flag and attempts a leader-lease fallback; otherwise it returns `DataIsNotReady`.

For `ReadIndexReplicaRead`, `try_local_follower_read()` decodes a nonzero read timestamp and internally attempts the stale-read path. If it cannot serve locally, it redirects to raftstore for normal read-index handling.

After local execution, the reader marks the read tracker as local, updates metrics, binds the delegate term to the response, attaches `txn_ext` and bucket metadata to snapshots, copies `txn_extra_op`, and invokes the callback. Redirects use `ProposalRouter`; full channels return `server_is_busy`, and disconnected channels return `region_not_found`.

## State and Persistence Behavior
This file does not persist raft or KV state. It reads from engine snapshots and from raftstore metadata maintained elsewhere. Its state is safety metadata and caches: per-thread delegate LRU, snapshot cache, delegate versions, lease timestamps, safe timestamps, and transaction/coprocessor attachments.

Snapshot timing is central. For cached reads, the engine snapshot is acquired before a monotonic timestamp is recorded, with a release fence between the two. The lease check uses that snapshot timestamp, ensuring the snapshot was created while the leader lease was valid. Delegate `last_valid_ts` invalidates reuse when metadata changes after the `ThreadReadId` was created.

Stale reads intentionally do not use the shared `SnapCache`; they use per-request snapshots so stale-read and normal local-read batches cannot invalidate each other incorrectly. `release_snapshot_cache()` clears the cached read ID and snapshot, releasing engine snapshot resources such as RocksDB sequence-number retention.

`ReadDelegate` source instances in `StoreMeta` own the version clock. Updating region/term/applied term/lease/buckets/wait-data or marking pending remove increments the version. Dropping the source delegate also increments, allowing local caches to discover removal.

## Dependencies and Integration Points
The local reader depends on raftstore peer metadata (`Peer`, `StoreMeta`, `RegionReadProgress`, `RemoteLease`, `LeaseState`, `TxnExt`), routing traits (`ProposalRouter`, `CasualRouter`), command/response types (`RaftCommand`, `Callback`, `ReadResponse`, `ReadContext`), and request policy inspection through `RequestInspector`.

Engine integration uses `KvEngine`, `Peekable`, snapshots, `SnapshotMiscExt::sequence_number()`, and `RegionSnapshot`. Coprocessor integration uses `CoprocessorHost::on_snapshot()` and bucket metadata from PD. Transaction integration uses `TxnExtraOp`, `WriteBatchFlags::STALE_READ`, and `TimeStamp`.

Safety validation relies on `util::check_store_id`, `check_peer_id`, `check_term`, `check_req_region_epoch`, `check_flashback_state`, `check_key_in_region`, `find_peer_by_id`, and `cmd_resp` helpers for errors and term binding. Metrics are emitted through local-read TLS metrics and `GLOBAL_TRACKERS`.

## Risks and Edge Cases
The fast path is correctness-sensitive. A local leader read is only safe if the snapshot was created within the matching-term leader lease; checking the lease before snapshot acquisition would be unsafe. The code's snapshot-then-lease ordering is intentional.

Delegate cache invalidation depends on `TrackVer` increments from every metadata change that can affect safety. Missing an increment would allow stale local metadata; excessive increments reduce cache effectiveness. `RegionBuckets` updates intentionally ignore older or equal versions.

Stale-read safety depends on decoding `flag_data` as a timestamp and checking safe ts before and after snapshot creation. If `flag_data` is malformed, follower-read cache falls back/redirects while stale-read policy can panic via `unwrap()` on decode. Safe ts lag greater than 200 ms triggers resolved-ts advancement notification.

Request validation has several non-obvious fallbacks: stale epochs redirect rather than error, missing delegates redirect, witness and wait-data states return errors, and flashback state can reject local reads. Replica reads without a usable nonzero read timestamp redirect to raftstore.

Snapshot cache lifetime can retain engine resources. Callers handling batched RPCs should release the cache when the batch ends; tests verify cached and noncached paths release oldest snapshot sequence numbers differently.

## Test Signals
The in-file test suite covers local read redirect versus execution, no-region cache misses, stale applied term, valid leader lease reads, store/peer/term/epoch mismatches, read quorum redirect, lease expiration, channel-full busy responses, lease term mismatch, delegate cache refresh after progress updates, source delegate removal invalidation, stale-read safe-ts success/failure, and leader fallback for stale reads.

It also covers `ReadExecutorProvider`, snapshot sharing across regions with the same `ThreadReadId`, snapshot cache invalidation when delegate `last_valid_ts` is newer than read ID creation, explicit snapshot cache release, stale reads bypassing shared cache, resolved-ts notification for stale reads, follower-read cache based on `read_index_safe_ts`, and follower-read fallback to raftstore.
