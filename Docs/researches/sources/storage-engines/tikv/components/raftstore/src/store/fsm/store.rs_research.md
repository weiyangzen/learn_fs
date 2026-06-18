# `sources/storage-engines/tikv/components/raftstore/src/store/fsm/store.rs`

## Purpose
This file is the store-level half of TiKV raftstore's batch-system runtime. It wires `PeerFsm` instances, the global `StoreFsm`, apply workers, asynchronous/synchronous raft log writers, PD/background workers, snapshot managers, transport, store metadata, and recurring store ticks into one `RaftBatchSystem`. It also owns the top-level raft message ingress path for messages whose target peer may not be registered yet.

## Important APIs, Types, and Functions
- `StoreRegionMeta` exposes store id, read delegates, region read progress, and range search for outside raftstore consumers.
- `StoreMeta` is the shared in-memory region map. It tracks `region_ranges`, `regions`, `readers`, pending raft messages, pending snapshots/merges, atomic snapshot destroy state, read progress, damaged file ranges/regions, and apply-catchup readiness counters.
- `RaftRouter<EK, ER>` wraps `BatchRouter<PeerFsm, StoreFsm>` and implements `ApplyNotifier`. It routes client raft commands, incoming raft messages, apply results, broadcasts, and control messages.
- `PollContext<EK, ER, T>` is the per-poller dependency bundle: config, store identity, routers, worker schedulers, engines, transport, metrics, snapshot manager, feature gate, store metadata, replication state, IO sender state, disk usage, latency inspectors, and GC safe point.
- `StoreFsm` is the singleton store control FSM with a loose-bounded receiver for `StoreMsg`.
- `StoreFsmDelegate` handles control messages and store ticks, including PD heartbeats, snapshot GC, compaction scheduling, imported SST cleanup, consistency checks, raft message rerouting/peer creation, replication-mode updates, unsafe recovery peer creation, and region wakeups.
- `RaftPoller` implements `PollHandler` for the batch system. It drains store and peer mailboxes, delegates peer work to `PeerFsmDelegate`, collects ready state, dispatches write work, flushes transports/metrics/tick batches, and updates busy signals.
- `RaftPollerBuilder::init` scans persisted region metadata from `CF_RAFT`, reconstructs peers, repairs applying snapshot state, clears tombstone metadata, registers meta/read-progress state, and deletes stale KV data ranges.
- `RaftBatchSystem::spawn`, `start_system`, and `shutdown` create, start, and stop raftstore workers and batch systems.
- `create_raft_batch_system` constructs the store and apply batch systems plus routers before full store bootstrap.

## Control Flow
Startup flows from `create_raft_batch_system` to `RaftBatchSystem::spawn`. `spawn` creates support workers, initializes the snapshot manager, region/snapshot/cleanup/PD/disk/fail-fast/write workers, then builds a `RaftPollerBuilder`. `RaftPollerBuilder::init` scans the KV engine's raft CF for `RegionLocalState`, drops tombstones, reconstructs normal/merging/unavailable peers, schedules applying snapshots, fills `StoreMeta`, and calls `clear_stale_data` for gaps outside known regions. `start_system` registers peer mailboxes, force-sends `PeerMsg::Start` to each peer, sends `StoreMsg::Start` to the store FSM, spawns raft and apply pollers, starts refresh-config and PD runners, and raises raftstore thread priority.

Runtime polling has three phases. `begin` refreshes dynamic config, buffer capacities, snapshot file limits, tick intervals, disk status, and write senders. `handle_control` drains bounded store messages and dispatches through `StoreFsmDelegate::handle_msgs`. `handle_normal` drains peer messages, delegates them to `PeerFsmDelegate`, collects ready state, and can skip expensive end processing when sync writes are enabled and no ready exists. `end` records latency-inspection timings, writes ready state synchronously or forwards inspectors to async write workers, marks the store busy if ready processing exceeds election timeout, and records process-ready metrics.

Incoming raft messages first try direct peer routing in `RaftRouter::send_raft_message`; if no peer route exists the message is sent to the store control mailbox as `StoreMsg::RaftMessage`. `StoreFsmDelegate::on_raft_message` retries direct routing, validates store id and epoch, handles tombstone/merge compatibility cases, calls `check_msg` against persisted `RegionLocalState`, possibly creates a peer through `maybe_create_peer`, or records a bounded pending first message for split races.

## State and Persistence Behavior
`StoreMeta` is in-memory but mirrors persisted region state. Region local state and raft state live in the KV engine raft CF and raft engine; startup reads them, writes cleanup batches for tombstones, recovers applying snapshot state through `peer_storage::recover_from_applying_state`, and consumes raft log batches synchronously where needed. `clear_stale_data` deletes KV data ranges not covered by any recovered region. Peer creation for replication registers memory metadata before mailbox registration, while unsafe recovery creation deletes stale data by key range, writes `PeerState::Normal` with sync write options, and then registers the peer.

Raft message memory is tracked through `MEMTRACE_RAFT_MESSAGES`; messages decrement trace on drop unless successfully forwarded. Router alive/leak counts are pushed to memory trace when peers are registered or closed. Periodic entry-cache eviction is configured here but actual eviction is handled in peer tick logic.

The file persists no user data directly outside repair, cleanup, unsafe recovery, and raft/write-worker setup paths. Most normal writes are batched through `StoreWriters` or sync write worker. Snapshot files are managed by `SnapManager` and cleanup/import SST workers, with stale import SST deletion governed by region epoch/version rules and an old-protocol one-week fallback.

## Dependencies and Integration Points
The file integrates `batch_system`, `engine_traits`, `kvproto`, `pd_client`, raft, resource control/metering, health controller latency inspection, failpoints, TiKV worker pools, snapshot/import subsystems, coprocessor region-change hooks, replication mode, fail-fast monitoring, async IO write/read routers, and PD reporting. It exports `RaftRouter` and `create_raft_batch_system` through `store/mod.rs`.

Store ticks depend on labels from `metrics.rs` and tick definitions from `msg.rs`. Hibernation and peer behavior are mostly delegated to `PeerFsmDelegate` and peer modules, but this file can broadcast unreachable/replication-mode/resolved-store events and awaken regions through raft messages.

## Risks and Edge Cases
- Lock ordering matters: comments require `store_meta` before `pending_create_peers` and before `global_replication_state`. Violating this can deadlock raftstore.
- `StoreMeta::set_region` panics if previous metadata is inconsistent while holding the meta lock.
- Peer creation must handle split, merge, overlapping ranges, damaged ranges, tombstones, and local-first races. Wrong ordering can register overlapping peers or lose first raft messages.
- `clear_stale_data` deletes gaps outside recovered regions at startup. Incorrect `region_ranges` reconstruction would make this destructive.
- The `pending_msgs` ring intentionally stores only bounded first messages; capacity pressure can discard old first messages.
- Unsafe recovery peer creation panics on write/delete failures after meta insertion, so partial failure handling depends on process abort/restart semantics.
- Metrics flushing is intentionally throttled; short test runs may not expose metric increments until flush.

## Test Signals
The file has one local unit test, `test_calc_region_declined_bytes`, validating compaction-range declined-byte attribution. Most important behavior is covered indirectly by raftstore integration tests elsewhere. Useful future test signals include startup recovery with applying/tombstone/merging states, local-first peer creation races, damaged range rejection, store heartbeat busy-on-apply transitions, and unsafe recovery peer creation persistence ordering.
