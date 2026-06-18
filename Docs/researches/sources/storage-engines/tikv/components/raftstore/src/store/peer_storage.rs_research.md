# sources/storage-engines/tikv/components/raftstore/src/store/peer_storage.rs

## Purpose
`peer_storage.rs` is the Raft storage adapter for a TiKV region peer. It implements the `raft::Storage` contract on top of TiKV's separated KV and Raft engines, owns the in-memory storage-facing view of region metadata, coordinates snapshot generation/application, and prepares `WriteTask`s for async persistence. The file is also responsible for local peer metadata initialization and cleanup, including crash-recovery paths where snapshot metadata may have been written to one engine but not the other.

## Important APIs, Types, and Functions
The key type is `PeerStorage<EK, ER>`, parameterized by `KvEngine` and `RaftEngine`. It wraps `Engines<EK, ER>`, the current `metapb::Region`, local peer identity, a `SnapState`, optional `GenSnapTask`, a region worker scheduler, retry counters, and an `EntryStorage<EK, ER>`. `Deref`/`DerefMut` expose `EntryStorage`, so methods such as `append`, `term`, `first_index`, `last_index`, `applied_index`, `raft_state`, and cache maintenance are integrated as if they belonged to `PeerStorage`.

`SnapState` models snapshot lifecycle: `Relax`, `Generating { canceled, index, receiver }`, `Applying(status)`, and `ApplyAborted`. `CheckApplyingSnapStatus` maps worker status atomics into peer-FSM decisions. Constants such as `RAFT_INIT_LOG_INDEX`, `RAFT_INIT_LOG_TERM`, `INIT_EPOCH_VER`, and job status integers encode bootstrap and snapshot-worker invariants.

Initialization flows through `PeerStorage::new`, `init_raft_state`, and `init_apply_state`. If a region is already initialized but lacks persisted state, the initial log index/term and applied/truncated state are seeded at `5`, which forces new followers to obtain a snapshot before normal log catch-up. `recover_from_applying_state` repairs a crash window by comparing a KV-side snapshot raft state with the raft-engine raft state and, if the snapshot state has a higher commit, cleaning raft logs and copying that state into the raft engine.

Snapshot APIs include `snapshot`, `validate_snap`, `need_gen_snap_precheck`, `cancel_generating_snap`, `apply_snapshot`, `handle_raft_ready`, and `persist_snapshot`. Metadata helpers include `clear_meta`, `clear_meta_in_kv_and_raft`, `write_initial_raft_state`, `write_initial_apply_state`, and `write_peer_state`. `do_snapshot` builds an actual raft snapshot via `SnapManager`.

## Control Flow
For normal raft reads, the raft crate calls the `Storage` implementation, which delegates entries and terms to `EntryStorage`. `initial_state` returns an empty `ConfState` for uninitialized peers with default hard state, otherwise derives the conf state from the current region. Snapshot requests enter `PeerStorage::snapshot`: witness leaders refuse snapshot generation, witness recipients can receive an empty snapshot if local apply has caught up, and normal recipients use an asynchronous generation task. Existing generation is polled with `try_recv`; stale, canceled, disconnected, or decode/epoch-invalid results cause retry or error. Retry count is capped by `MAX_SNAP_TRY_CNT`.

Incoming raft `Ready` values are handled by `handle_raft_ready`. It creates a `WriteTask`, applies a non-empty ready snapshot into that task, appends ready entries, updates hard state when appropriate, and records a raft-state write only when state changed or a snapshot is present. For snapshots, it also writes a KV copy of the snapshot raft state and the apply state so restart recovery can bridge the KV/raft engine write ordering.

Applying a snapshot decodes `RaftSnapshotData`, verifies region id, prepares raft/KV write batches, clears existing metadata if initialized, tombstones overlapped destroy regions, writes the new `RegionLocalState` as `Applying` unless it is a witness snapshot, and updates last/applied/truncated indexes and terms in memory. `persist_snapshot` then schedules actual data cleanup/application work, handles source-region extra-data cleanup for merges, bypasses the async apply worker for witness snapshots, and finally updates the stored region.

Destroy flow is split between in-peer scheduling and worker-side synchronous cleanup. `schedule_destroy_peer` clears entry caches and force-schedules `RegionTask::ClearPeerMeta`. `clear_meta_in_kv_and_raft` coordinates with `StoreMeta` and `pending_create_peers`, writes KV tombstone state with sync write options, then consumes the raft log batch synchronously.

## State and Persistence Behavior
This file spans three state surfaces: in-memory `PeerStorage`/`EntryStorage`, KV CF_RAFT metadata, and raft-engine logs/state. KV metadata includes region state, apply state, and temporary snapshot raft state. Raft engine state includes `RaftLocalState` and raft logs. Persistence order is deliberate: snapshot apply writes KV state that can survive a crash before raft-engine state is consumed; peer destroy writes tombstone metadata to KV first with sync enabled, then consumes raft cleanup. The code comments call out crash windows and explain why `recover_from_applying_state` exists.

Snapshot generation registers `SnapEntry::Generating` with `SnapManager`, validates the KV snapshot's apply state against the caller-supplied last applied state, verifies the region is still `PeerState::Normal`, builds snapshot files, and serializes `RaftSnapshotData` into raft snapshot data. Snapshot cancellation uses atomics shared with generation workers and optional compaction indexes to avoid canceling still-valid snapshots.

## Dependencies and Integration Points
The module integrates `engine_traits`, `kvproto` raft/metapb messages, `raft::Storage`, `EntryStorage`, async IO `ReadTask`/`WriteTask`, region workers, `SnapManager`, `StoreMeta`, peer utilities, metrics, failpoints, and TiKV key encoders. `read_queue.rs` and `simple_write.rs` sit elsewhere in peer request flow, while `region_snapshot.rs` uses `PeerStorage::raw_snapshot` and `PeerStorage::region` to build bounded read snapshots.

## Risks and Edge Cases
The highest-risk areas are cross-engine persistence ordering, snapshot staleness validation, witness snapshot special cases, destroy/create races under local first replicate, and cleanup of extra data around merge/split ranges. `clear_meta_in_kv_and_raft` contains panics for inconsistent pending-create state. `handle_raft_ready` intentionally skips hard-state persistence when `last_index == 0`, so incorrect initialization could suppress necessary persistence. Snapshot retry accounting is subtle: canceled attempts do not always increment `snap_tried_cnt`, unknown peers do not count, and disconnected generation channels trigger retries.

## Test Signals
Tests cover term lookup, metadata cleanup, async entry fetch fallback, compaction boundaries, snapshot generation retry/staleness/cancellation behavior, multi-file snapshot layout for TiKV/TiFlash/witness roles, snapshot application state transitions, cancel/check apply snapshot status transitions, and validation failures for inconsistent raft/apply state. These tests exercise both in-memory invariants and persisted engine state.
