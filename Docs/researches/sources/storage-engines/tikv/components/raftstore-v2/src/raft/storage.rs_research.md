# sources/storage-engines/tikv/components/raftstore-v2/src/raft/storage.rs

Purpose: this file implements raftstore-v2 storage, analogous to v1 `PeerStorage`, and provides the `raft::Storage` trait over TiKV raft-engine entry storage plus region/tablet metadata.

Important APIs/types/functions: `Storage<EK, ER>` owns `EntryStorage`, current peer, `RegionLocalState`, persistence flags, dirty-data flag, snapshot states/tasks, split-init state, apply trace, and flushed epoch. `Storage::create` constructs storage from local states. Methods expose entry/region/peer state, generation task management, dirty mark, flushed epoch, split-init, raft/apply state, initialization status, tablet index, region-state replacement, and replay-count estimate. The `raft::Storage` impl supplies `initial_state`, `entries`, `term`, `first_index`, `last_index`, and `snapshot`.

Control flow: creation finds the local peer in the region, reads dirty mark for the current tablet index, creates `EntryStorage`, and initializes snapshot/task containers. `initial_state` asserts hard-state commit matches initialization status; uninitialized peers return empty conf state even if hard state exists, while initialized peers return region-derived conf state. Snapshot calls delegate to the snapshot logic in `operation/ready/snapshot.rs`.

State and persistence: `ever_persisted` marks whether initial state must be persisted even if unchanged. `has_dirty_data` survives through raft engine dirty marks and suppresses snapshot generation after split until cleanup. `apply_trace` records flushed/applied indexes for replay/log GC. `flushed_epoch` advances only when a newer epoch is persisted.

Dependencies/integration: depends on `EntryStorage`, raft protobuf states, read scheduler, raft metrics, TiKV utility peer lookup, and operation types `ApplyTrace`, `GenSnapTask`, `SnapState`, and `SplitInit`.

Risks: the hard-state/initialized assertion protects a key v2 invariant; violating it means raft can start with wrong conf state. Dirty mark correctness affects snapshot availability and split recovery. Snapshot state is in `RefCell`, so runtime borrow discipline matters.

Test signals: local tests exercise snapshot apply, snapshot generation, cancellation, stale result handling, and storage creation with test engines/tablet registry.
