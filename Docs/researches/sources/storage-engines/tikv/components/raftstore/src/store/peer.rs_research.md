# Research: sources/storage-engines/tikv/components/raftstore/src/store/peer.rs

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008852`: lines 1-6535, `Docs/researches/chunks/subset-b-008852_research.md`
- `subset-b-008853`: lines 6536-7003, `Docs/researches/chunks/subset-b-008853_research.md`

## Chunk Research

### subset-b-008852: lines 1-6535

# sources/storage-engines/tikv/components/raftstore/src/store/peer.rs lines 1-6535

## Scope and Purpose

This chunk contains the main Raftstore `Peer<EK, ER>` implementation for a TiKV region replica. It defines the peer's proposal queues, read-index queue integration, leader lease handling, Raft ready append/advance flow, snapshot persistence/application handoff, destroy lifecycle, split/merge gates, disk-full quorum handling, transfer-leader protocol, PD heartbeat payloads, and request inspection policy. The final lines enter the local test module, but the actual test bodies are outside this requested line range.

`Peer` is the stateful bridge between raft-rs `RawNode<PeerStorage<EK, ER>>`, TiKV's apply FSM, async/sync write IO, transport, PD reporting, coprocessor hooks, region read progress, transaction extensions, and region-worker tasks. Most functions in this chunk are about preserving the exact order between Raft state changes, durable persistence, apply scheduling, message sending, and externally visible reads.

## Important Types and State

- `ProposalQueue<C>` tracks pending proposals in `(term, index)` order. It supports tracker lookup, proposal-time lookup, stale-proposal notification, callback extraction when entries commit, and capacity shrinking after drains. It panics if committed entries disagree with queued proposal ordering, which is a strong consistency invariant.
- `ProposalContext` serializes raft entry flags into one byte: sync-log, split, prepare-merge, commit-merge, and rollback-merge. It is attached to `Entry.context` and later used in commit handling and failpoints.
- `CmdEpochChecker<S>` records at most a small deque of proposed epoch-changing admin commands. It prevents conflicting epoch checks before apply catches up, attaches callbacks to rejected commands, advances callbacks after apply, and reports stale callbacks on term changes or drop.
- `ApplySnapshotContext`, `PersistSnapshotResult`, `UnpersistedReady`, and `ReadyResult` describe the ready/snapshot persistence pipeline: ready number, messages to send after snapshot apply, persisted snapshot metadata, pending async ready numbers, and whether append processing produced IO.
- `SplitCheckTrigger` accumulates approximate size/key state, compaction-declined bytes, ingest effects, and skip flags for split checks.
- `Peer<EK, ER>` holds the core replica state: region and peer metadata, `RawNode`, proposal/read queues, leader lease, pending snapshot/apply state, merge/split markers, replication mode and group commit state, disk-full peers, transaction extension state, read-progress tracker, write router, unpersisted ready queues, leader-transfer state, recovery state, and operational counters.
- `DiskFullPeers` tracks peers on almost-full/already-full stores and whether each can still contribute to quorum; `majority` marks when disk-full peers affect the quorum set.
- `RequestPolicy` and `RequestInspector` decide whether a command is handled as local read, stale read, read index, normal proposal, transfer leader, or conf change.
- `TransferLeaderContext` serializes pre-transfer metadata: empty context, command-reply marker, or coprocessor-provided key/value context. `TransferLeaderState` tracks current transferee, pending pre-transfer message deadline, and entry-cache warmup state.

## Core Control Flow

Peer construction (`Peer::new`) validates the peer id, builds `PeerStorage`, initializes raft-rs `RawNode` with TiKV config, seeds applied and last-index derived fields, initializes read progress and transaction extensions, optionally campaigns for a single-peer region, and syncs the persisted index cache. `activate` registers the peer with apply scheduling and emits a coprocessor region-create event.

Raft message flow starts with `step`, which updates heartbeat/leader-missing observations, short-circuits read-index requests when a valid leader lease can answer them, drops unsafe early vote messages, calls `RawNode::step`, reports commit timing, and flags balance-related snapshot generation. Outbound messages are wrapped by `build_raft_message`/`prepare_raft_message`, enriched with region epoch, peer metadata, disk usage, and initial-message range keys, then sent through `send_raft_messages`, which reports unreachable peers and snapshot failures back to raft-rs.

Ready append flow is centered on `handle_raft_ready_append`. It refuses work while pending destroy or snapshot application blocks readiness, checks pending snapshot prerequisites, waits for overlapping atomic snapshot source destruction, obtains `RawNode::ready`, updates metrics, applies role/leader-commit side effects before external messages, sends leader messages, advances read-index requests, schedules committed entries to apply, handles generate-snapshot tasks, persists ready data through `PeerStorage::handle_raft_ready`, and either dispatches a write task or advances non-IO ready state immediately.

Ready advance flow has separate async and sync paths. `on_persist_ready` consumes `unpersisted_readies`, sends persisted messages only after durability, calls `RawNode::on_persist_ready`, updates persisted caches, forwards forced-leader commit indexes, and schedules snapshot application once the snapshot ready is fully persisted. `handle_raft_ready_advance` performs the same ordering for sync write worker mode using `advance_append`/`advance_append_async`, handles light ready commit/messages/committed entries, and updates storage commit state when the light ready changes commit index.

Committed entry handling (`handle_raft_committed_entries`) asserts that no snapshot is being applied, updates raft log size hints and term cache per entry, renews leader lease based on the proposal time of a committed current-term command, extracts proposal callbacks, invokes "committed" callbacks only when epoch safety was guaranteed, builds an `Apply` task with commit index bounded by persisted index, traces/evicts entry cache as needed, and schedules apply through `apply_router`.

Apply completion (`post_apply`) advances raft-rs applied index, advances the epoch checker, compacts follower entry cache, persists apply state and applied term into `PeerStorage`, updates hot-write and split-check hints, unblocks pending snapshots/read-index requests, updates `RegionReadProgress`, and notifies coprocessors/read delegates when a leader applies the current term.

## Reads, Leases, and Read Progress

`RequestInspector::inspect` rejects mixed read/write batches and invalid command types, routes stale reads directly, replica reads through follower read-index policy, read-quorum requests through read index, and ordinary reads through local lease only when the peer has applied the current term and the lease is valid.

Local reads call `handle_read` directly with the peer storage commit index. `handle_read` optionally checks region epoch, enforces stale-read `safe_ts`, asks `RegionReadProgress` to advance resolved-ts when stale read lag is material, executes the read through a `PollContextReader` snapshot, attaches `txn_ext` and bucket metadata to returned snapshots, includes `txn_extra_op`, and binds the current raft term to the response.

Read-index flow (`read_index`, `apply_reads`, `response_read`, and `post_pending_read_index_on_replica`) is careful about leader and follower semantics. Leaders can amend compatible reads into the last pending read while the prior lease window covers them. Followers reject replica reads when local disk is not normal, wake hibernated leaders and ask PD for leader info when no leader is known, retry lost read-index requests, and only serve unsafe replica reads after applying to the read index, with no pending merge and no snapshot handling. Leader reads wait for `ready_to_handle_read`, which blocks during split, merge, or before the current term is applied.

Lease renewal is centralized in `maybe_renew_leader_lease`, guarded by `should_renew_lease`. Leaders do not renew while splitting, merging, in force-leader mode, or in flashback state. Lease updates propagate to read delegates through `ReadProgress`, and `need_renew_lease_at` avoids redundant renewals when pending reads or writes already cover the next heartbeat window.

## Snapshot, Destroy, Split, and Merge Behavior

Snapshot handling is deliberately serialized. `check_snap_status` blocks new ready processing until a persisted snapshot is scheduled and applied; on success it sends delayed messages, advances apply index to the truncated index, advances the epoch checker, finishes recovery wait states, resumes read progress, updates applied progress, and clears `wait_data` peers by notifying the leader and scheduling apply recovery.

`handle_raft_ready_append` records snapshot results in `apply_snap_ctx`, pauses read progress, resets raft-log size hints, schedules best-effort raftlog GC for stale logs, and handles witness snapshot notifications. `on_persist_snapshot` validates ready number ordering, marks the snapshot scheduled, persists snapshot metadata into storage, refreshes peer metadata that may have changed from learner/witness transitions, adjusts raft priority, and activates the peer.

Destroy flow starts with `maybe_destroy`, which defers destruction while atomic snapshot or snapshot apply/persist work is in flight, cancels applying snapshots where possible, marks `pending_remove`, and returns a `DestroyPeerJob`. `destroy` schedules background peer metadata/data cleanup through storage, falling back to synchronous `clear_meta_in_kv_and_raft` if the worker is unavailable. `ready_to_destroy` records cleanup metrics, schedules data clearing when needed, clears pending reads, and reports all pending proposals as region removed.

Merge safety is spread across proposal and read logic. `pre_propose_prepare_merge` checks follower progress, rejects pending snapshots, bounds log and entry-size gaps, rejects conf/admin commands in the merge gap, gates in-memory pessimistic locks behind `prepare_merge_fence`, and proposes those locks before PrepareMerge. `on_leader_commit_idx_changed` records committed split/prepare-merge indexes before commit index is externally observable; PrepareMerge suspects the lease and discards read progress to avoid stale local reads. `maybe_append_merge_entries` appends source entries directly during commit-merge handling and adjusts term/commit metadata if needed.

## Proposals, Conf Changes, and Transfer Leader

`propose` is the public command entry point. It inspects the request, dispatches reads immediately, routes transfer-leader/admin/conf-change/normal proposals, checks disk-full policy, handles epoch conflicts by attaching callbacks to conflicting admin commands, invokes proposed callbacks only after current-term apply safety, marks urgent proposals to disable lazy commit, records proposal metadata, and disables unpersisted apply for PrepareMerge.

`propose_normal` rejects inappropriate force-leader and merging states, requires current-term apply for admin commands, runs `CmdEpochChecker`, invokes coprocessor `pre_propose`, serializes and size-checks the request, calls raft-rs `propose`, handles silent drops as NotLeader, and relaxes max-inflight limits for merge proposals when disk-full peers must receive logs.

`propose_conf_change` requires no pending merge/conf change and current-term apply, runs coprocessor checks and epoch checks, serializes the admin command, and delegates to `propose_conf_change_internal`. The internal path uses `util::check_conf_change` for health/removal constraints and calls raft-rs `propose_conf_change` with sync-log context.

Transfer leader uses a pre-transfer protocol. The leader sends `MsgTransferLeader` with last-log term, cache low index, and serialized `TransferLeaderContext`; the transferee rejects if it is learner/witness/wait-data, applying snapshot, contacted by a nonleader, or less disk-healthy than the source. It may warm entry cache asynchronously, then acks with applied index/log term. The leader validates voter status, snapshot state, pending conf index, and max log lag before calling raft-rs `transfer_leader`. TransferLeader admin commands may choose the best matched transferee and return an immediate admin response because the actual leadership move is advisory.

## Replication, Disk-Full, PD, and Extra Messages

Replication mode support initializes and switches group commit based on `GlobalReplicationState` and DR auto-sync status. `region_replication_status` checks group commit consistency, enables group commit after SyncRecover catch-up, and reports `IntegrityOverLabel`, `SimpleMajority`, or `Unknown` to PD. `check_group_commit_consistent` temporarily enables group commit to query maximal committed index, then restores the original setting.

Leader heartbeat support includes `check_peers`, `collect_down_peers`, `collect_pending_peers`, `any_new_peer_catch_up`, `check_stale_state`, `heartbeat_pd`, and stale-peer extra messages. PD heartbeats carry term, region, down/pending peers, write stats, approximate size/keys, replication status, and wait-data peers.

Disk-full handling refills `DiskFullPeers` from store disk usage and raft progress, adjusts per-peer max inflight to zero/one/full depending on quorum contribution and merge needs, marks dangerous majority sets containing already-full peers, rejects proposals when the leader or quorum cannot accept them, and may pre-transfer leadership to a normal peer to preserve write availability.

Extra-message integration covers wake-up broadcasts for hibernated regions, stale-peer checks, snapshot-generation precheck request/response, availability notification after wait-data snapshot apply, want-rollback-merge messages, and max-ts update scheduling on leadership acquisition.

## Persistence and Ordering Guarantees

The central persistence invariant is that messages depending on durable state are sent only after the corresponding ready has been persisted. Async write mode stores ready numbers in `unpersisted_readies`; no-IO ready instances are attached to the prior IO ready where possible. Sync write mode holds `unpersisted_ready` until `handle_raft_ready_advance`.

Committed apply tasks use a commit index capped at the persisted index so apply forwarding cannot advertise unpersisted logs. Snapshot ready application is delayed until the snapshot's ready number is persisted and all earlier unpersisted readies are consumed. Read progress is paused during snapshot apply and resumed only after apply completion advances storage and raft-rs state.

Unpersisted apply is disabled on term change and PrepareMerge by setting a minimum safe index, then re-enabled only after applying beyond that index and only when configured. Metrics track whether raft-rs currently has unpersisted apply enabled to keep gauges balanced even if raft-rs resets the limit on demotion.

## Dependencies and Integration Points

- raft-rs: `RawNode`, `Ready`, `LightReady`, `Entry`, `Message`, progress state, conf voters, read index, leader transfer, group commit, persisted/committed/applied indexes.
- Storage: `PeerStorage`, `Engines`, `KvEngine`, `RaftEngine`, snapshots, term cache, apply state, raft state, entry cache, snapshot persistence, destroy scheduling, log GC, and async entry-cache warmup.
- FSM and workers: `PollContext`, `ApplyTask`, `Apply`, `WriteRouter`, `WriteMsg`, region worker tasks, split-check tasks, raftlog GC tasks, and read tasks.
- Transport and routing: `Transport`, `RaftMessage`, `ExtraMessage`, `RaftStoreRouter`, `PeerMsg`, `CasualMessage`, read command forwarding, and apply router scheduling.
- PD/coprocessor: PD heartbeat/update-max-ts/query-leader tasks, replication state, coprocessor region-change/role-change/pre-propose/pre-transfer hooks, and read-progress callbacks.
- Transaction/read support: `TxnExt`, in-memory pessimistic locks, `LocksStatus`, `TxnExtraOp`, `ReadDelegate`, `RegionReadProgress`, stale-read safe timestamps, bucket metadata.
- Operational controls: failpoints, metrics, memory tracing, disk usage, feature gate for snapshot-generation precheck, hibernation group state, unsafe recovery, and snapshot backup recovery.

## Risks and Edge Cases

- Ready ordering is fragile: sending messages before persistence, advancing ready numbers out of order, or handling new ready while a snapshot is applying can violate raft durability or create stale reads. The code uses assertions, panics, and queues to enforce this.
- Lease correctness depends on split/merge ordering. Split and PrepareMerge commit indexes must be recorded before the new commit index leaks through heartbeat/read-index responses; otherwise local reads can serve stale ranges.
- Proposal callback correctness depends on monotonic `(term, index)` ordering in `ProposalQueue` and accurate `CmdEpochChecker` state. Term changes intentionally stale outstanding callbacks.
- Direct merge-entry append bypasses normal raft replication paths; term and commit metadata are manually adjusted to keep raft state coherent.
- Disk-full handling trades availability and safety by throttling peers, selectively allowing quorum contributors, and special-casing merge proposals. Incorrect quorum classification can either halt writes unnecessarily or send logs to stores that cannot persist them.
- Transfer leader is multi-stage and advisory. Stale cache-warmup state, pending conf changes, pending snapshots, learner/witness targets, disk-health skew, and version-skewed missing low indexes are all handled explicitly.
- Follower read-index requests can be lost and must be retried; unsafe replica reads are blocked by apply lag, pending merge, and snapshot handling. A long gap returns `ReadIndexNotReady`.
- Destroy during snapshot work is deferred via flags. Incorrectly clearing data while snapshot apply or atomic snapshot overlap is active could delete live region data.
- Several paths panic rather than recover after storage/ready invariant failures, because continuing could resurrect stale peers or corrupt Raft state.

## Test Signals

The chunk begins the local test module at line 6533, so test bodies are outside this work item's range. The visible production code has many failpoints and metrics that indicate intended test coverage:

- Proposal queue tests should verify monotonic push, stale callback notification, exact term/index matching, queue shrinking, and panic on unexpected callback index.
- Epoch checker tests should cover conflicting split/merge/change-peer commands, term changes, callback attachment to conflict commands, apply advancement, and drop-time stale notification.
- Read policy tests should cover local lease reads, read quorum, replica reads, stale reads, mixed read/write rejection, invalid command rejection, and current-term apply gating.
- Ready pipeline tests should exercise async and sync persistence, no-IO ready attachment, persisted message sending after durability, light ready commit handling, and panic cases for out-of-order ready numbers.
- Snapshot tests should cover pending snapshot gating, `apply_snap_ctx` scheduling, read-progress pause/resume, wait-data recovery, witness snapshot notification, stale-log GC scheduling, and destroy deferral during snapshot work.
- Lease/split/merge tests should verify no lease renewal during split/merge/force-leader/flashback, lease suspicion after PrepareMerge, safe-ts discard, prepare-merge fence behavior, pessimistic-lock proposal before merge, and log-gap/admin-command rejection.
- Disk-full tests should cover leader full rejection, follower full quorum classification, dangerous majority sets, max-inflight adjustments, merge proposal exceptions, and leader-transfer attempts away from full leaders.
- Transfer-leader tests should cover pre-transfer context serialization, rejection predicates, cache warmup timeout/staleness, command-reply ACK context, pending-conf/log-gap checks, and immediate command response behavior.
- PD/extra-message tests should cover down/pending peer reporting, stale-peer message peer-list caching, wake-up throttling, snapshot-generation precheck feature gating, availability response after wait-data snapshot, and replication status transitions.

## Cross-Chunk Notes

Lines after 6535 contain the test bodies for helpers and peer behaviors introduced here. The final reconciled per-file document should merge those tests with this production-code analysis, and should also account for any later `peer.rs` code beyond the requested line range.

### subset-b-008853: lines 6536-7003

# sources/storage-engines/tikv/components/raftstore/src/store/peer.rs lines 6536-7003

## Scope

This chunk covers the entire `#[cfg(test)] mod tests` at the end of TiKV raftstore's `store/peer.rs`. The selected lines are not production peer logic; they are unit tests for production helpers and local invariants defined earlier in the same file:

- synchronous-log and urgent-admin-command classification;
- one-byte `ProposalContext` raft-entry metadata encoding;
- `RequestInspector` policy selection for admin, read, write, stale-read, replica-read, read-quorum, and invalid request batches;
- `ProposalQueue` ordering, proposal lookup, stale-removal, propose-time lookup, and committed-callback behavior;
- `CmdEpochChecker` conflict tracking for proposed epoch-changing admin commands;
- `TransferLeaderContext` wire encoding and decoding.

Because this is a terminal file chunk, it also confirms that `peer.rs` ends at line 7003. The tests import `protobuf::ProtobufEnum`, `super::*`, `crate::store::msg::ExtCallback`, and `crate::store::util::u64_to_timespec`, then exercise private items through Rust's child-module visibility.

## Purpose

- Lock down which `AdminCmdType` values force raft log synchronization via `get_sync_log_from_request()`.
- Lock down which admin commands are considered urgent by `is_request_urgent()`, which affects follower lazy-commit behavior.
- Verify that `ProposalContext` flags round-trip through the compact byte-vector representation stored in raft entry context bytes.
- Verify `RequestInspector::inspect()` classifies requests into local read, stale read, read-index, normal proposal, transfer-leader proposal, and conf-change proposal paths, and rejects unsupported or mixed batches.
- Verify `ProposalQueue` can locate proposals by `(term, index)`, remove stale/front proposals as committed entries are processed, and preserve associated propose-time metadata.
- Verify uncommitted proposals from a previous term do not have their "committed" extension callback fired when later-term committed entries pass through the queue.
- Verify `CmdEpochChecker` serializes conflicting epoch-sensitive proposals, wakes waiters when conflicts apply, clears state on term advance, and reports stale callbacks on drop.
- Verify `TransferLeaderContext` remains backward-compatible for empty context, command-reply context, and custom coprocessor key/value context payloads.

## Important APIs, Types, And Functions

- `get_sync_log_from_request(&RaftCmdRequest) -> bool` returns true for admin commands that should synchronously persist raft logs before response. The test treats all admin types except `InvalidAdmin`, `CompactLog`, `TransferLeader`, `ComputeHash`, `VerifyHash`, `BatchSwitchWitness`, and `UpdateGcPeer` as sync-log commands.
- `is_request_urgent(&RaftCmdRequest) -> bool` is private and returns true for split, batch split, conf-change, conf-change-v2, compute/verify hash, prepare/commit/rollback merge, and batch switch witness admin commands. Non-admin requests are non-urgent.
- `ProposalContext` is a `bitflags` byte with `SYNC_LOG`, `SPLIT`, `PREPARE_MERGE`, `COMMIT_MERGE`, and `ROLLBACK_MERGE`. `to_vec()` emits either an empty vector or a single-byte bitset; `from_bytes()` accepts only empty or one-byte slices.
- `RequestPolicy` enumerates dispatch decisions: `ReadLocal`, `StaleRead`, `ReadIndex`, `ProposeNormal`, `ProposeTransferLeader`, `ProposeConfChange`, and `ReadIndexReplicaRead`.
- `RequestInspector` is a trait used by `Peer` and tests. It supplies `has_applied_to_current_term()` and `inspect_lease()`, while the default `inspect()` implementation performs request classification and lease/read-index decisions.
- `DummyInspector` in the test module is a minimal `RequestInspector` implementation with configurable applied-term and lease state. It isolates the policy logic from real peer state.
- `ProposalQueue<C>` stores ordered `Proposal<C>` values in a `VecDeque`. It supports `push()`, `find_propose_time()`, `pop()`, `find_proposal()`, `oldest()`, `back()`, and `gc()`.
- `Proposal<C>` comes from the raftstore FSM layer and carries `is_conf_change`, `index`, `term`, `cb`, optional `propose_time`, epoch-check metadata, and a `sent` marker.
- `Callback<S>` is the raft command callback type. These tests use write callbacks, extension callbacks, and panic/test snapshot types to assert callback invocation behavior without needing a live raftstore.
- `CmdEpochChecker<S>` tracks proposed admin commands whose application will change region epoch. It exposes local methods `propose_check_epoch()`, `post_propose()`, `last_cmd_index()`, `advance_apply()`, and `attach_to_conflict_cmd()`.
- `ProposedAdminCmd<S>` records a pending admin command's `AdminCmdType`, `AdminCmdEpochState`, raft index, and callbacks waiting on that conflict.
- `admin_cmd_epoch_lookup()` maps admin command types to whether they check or change region version/conf-version. The tests rely on its split and change-peer behavior.
- `TransferLeaderContext` is the raft message context for transfer-leader messages. It supports `None`, `CommandReply`, and `Custom(Vec<TransferLeaderCustomContext>)`.
- `TransferLeaderContext::to_bytes()`, `from_bytes()`, and `get_custom_ctx()` encode/decode context bytes using a leading tag and varint-length key/value pairs for custom coprocessor data.

## Control Flow

`test_sync_log()` iterates over every protobuf `AdminCmdType` value. For each type it builds a `RaftCmdRequest` with that admin command and asserts that `get_sync_log_from_request()` matches the hard-coded whitelist of non-sync-log admin commands. This guards against new admin command variants silently changing persistence semantics: a newly added protobuf enum value will be included by `AdminCmdType::values()` and will fail unless the helper classification and test expectation are updated consistently.

`test_urgent()` follows the same enum-wide pattern for `is_request_urgent()`. It marks split, conf-change, hash, merge, and witness-switch commands as urgent and asserts every other admin command is not urgent. It also checks a default non-admin `RaftCmdRequest` is not urgent. This covers the branch used by proposal handling to bypass follower lazy-commit delay for operations where prompt follower application matters.

`test_entry_context()` constructs several flag combinations containing a single structural context bit plus optional `SYNC_LOG`. It serializes each `ProposalContext` with `to_vec()`, parses it back with `from_bytes()`, and verifies all selected flags remain set. The test does not cover `ROLLBACK_MERGE`, empty context, unknown-bit truncation, or invalid multi-byte input, but it covers the context combinations produced by the `pre_propose()` match arms for split, prepare merge, and commit merge plus sync-log insertion.

`test_request_inspector()` builds a table of request/policy pairs, then runs it across all combinations of `applied_to_index_term` in `{true,false}` and `LeaseState` in `{Expired,Suspect,Valid}`. Admin requests are classified first: empty admin request is a normal proposal, change-peer and change-peer-v2 are conf changes, and transfer leader is a transfer-leader proposal. Non-admin writes become normal proposals. Read-only `Get` and `Snap` requests start as local reads but are downgraded to read-index unless the peer has applied the current term and the lease is valid. Stale-read flags override ordinary read handling and return `StaleRead`. Read-quorum forces `ReadIndex` even under a valid lease. Invalid command batches containing `Prewrite`, `Invalid`, or a mixture of read and write requests return errors.

`test_propose_queue_find_proposal()` fills a `ProposalQueue` with ordered proposals whose terms are derived from log index ranges. It then repeatedly appends one more proposal, checks that `find_propose_time()` returns the expected timestamp for every proposal not previously removed, calls `find_proposal()` for progressively increasing committed indexes, and verifies those proposals are removed from the queue. This exercises the core invariant that `find_proposal()` may discard all proposals in front of or at the searched `(term,index)` and that removed proposals are no longer visible through either `pop()` or `find_propose_time()`.

`test_uncommitted_proposals()` builds a queue with only term-1 proposals for entries `(1,1)` through `(5,1)`, while the simulated committed log sequence also includes later term-2 entries. It marks callbacks for committed term-1 entries as "must call" and callbacks for uncommitted term-1 entries as "must not call". Iterating through entries and invoking `find_proposal(term,index,0)` only finds matching term/index proposals. The term-1 proposals that were not committed before the term change must be notified stale by `find_proposal()` rather than having their committed extension callback invoked. The custom `DropPanic` helper makes missed or unexpected callback invocation fail the test.

`test_cmd_epoch_checker()` starts with an empty checker and a default region. It proposes a batch split at index 5 and verifies that ordinary requests and prepare-merge conflict with that version-changing command, while change-peer initially does not. It then proposes change-peer at index 6 and verifies conf-version-sensitive requests conflict with index 6, while ordinary version-sensitive requests still conflict with the earlier split at index 5. Applying through index 4 leaves both pending commands. Applying index 5 removes the split, wakes callbacks attached to it with an epoch-not-match response, and leaves the change-peer conflict. Advancing the term clears pending state and reports stale callbacks. The test also attaches multiple callbacks to one conflict index, verifies all are invoked on apply, verifies term advance invokes stale callbacks, and verifies `Drop` does the same outside shutdown.

`test_transfer_leader_context()` validates three encoding forms. `None` serializes to empty bytes and parses from empty bytes. `CommandReply` serializes to the singleton transfer-leader command-reply tag and parses back. `Custom` serializes a tagged sequence of varint-length-prefixed key/value entries, parses back to an equal value, and supports lookup by key with `get_custom_ctx()`.

## State And Persistence Behavior

- These tests do not directly write RocksDB, raft engine files, region metadata, or raft logs. Their persistence relevance is indirect: they pin helper decisions that determine raft entry context bytes, synchronous raft-log persistence, proposal lifecycle, and transfer-leader message context bytes.
- `get_sync_log_from_request()` influences whether proposed raft commands set `ProposalContext::SYNC_LOG` in `pre_propose()`. That context byte is persisted as raft entry context and later consumed when ready entries are applied or persisted.
- `ProposalContext::to_vec()` is the storage format for raft entry context metadata. The format is intentionally compact: empty for no flags, one byte for all currently supported flags. Any change from one-byte encoding affects raft-entry compatibility and should be treated as a wire/storage format change.
- `is_request_urgent()` affects in-memory scheduling/commit urgency. It does not persist state by itself, but a wrong classification can delay follower application for split/merge/conf-change style commands.
- `RequestInspector` reads applied-term and lease state but does not mutate persistent storage. In production `Peer` implementation, `has_applied_to_current_term()` compares peer storage applied term with raft term, and `inspect_lease()` can expire in-memory leader lease state if the lease is observed expired.
- `ProposalQueue` is in-memory leader-side state mapping raft log entries back to client callbacks and timing trackers. `find_proposal()` removes front proposals as entries are committed or proven stale; stale proposals are reported through `apply::notify_stale_req()`.
- `Callback::invoke_committed()` is used only when a matching proposal is known committed. The uncommitted proposal test guards against invoking committed extension callbacks for proposals superseded by later-term entries.
- `CmdEpochChecker` is in-memory gating state for proposals whose effects change region epoch. It holds callbacks for requests rejected behind a conflicting admin command, then reports `EpochNotMatch` when the conflicting command applies. It drains and reports stale callbacks on term changes or drop.
- `CmdEpochChecker::advance_apply()` builds an error response containing the current region epoch and binds the current term. This response is returned through callbacks rather than persisted.
- `TransferLeaderContext` bytes travel in raft messages, not region metadata. The custom context format is nevertheless a wire contract between transfer-leader observers/coprocessors and raftstore message handling.

## Dependencies And Integration Points

- The tests depend on protobuf enum iteration through `protobuf::ProtobufEnum`, which makes command-classification tests sensitive to new `AdminCmdType` variants.
- They depend on `kvproto::raft_cmdpb` request/response types: `RaftCmdRequest`, `Request`, admin subrequests, `AdminCmdType`, and `CmdType`.
- `RequestInspector` integrates with `WriteBatchFlags` from `txn_types`; the stale-read flag and transfer-leader proposal flag alter policy selection.
- Read policy decisions integrate with raft lease machinery through `LeaseState` and, in production, with `Peer::leader_lease`, `raft_group.raft.in_lease()`, and applied term from peer storage.
- `ProposalQueue` integrates with apply processing. Production paths call `find_propose_time()` and `find_proposal()` while handling committed entries, and waterfall metrics use proposal trackers for timing.
- `apply::notify_stale_req()` is the failure path for stale proposals and epoch-checker callbacks on term changes or checker drop.
- `CmdEpochChecker` integrates with `admin_cmd_epoch_lookup()`, `AdminCmdEpochState`, normal request epoch-check constants, and proposal paths that call `propose_check_epoch()` before raft proposal and `post_propose()` after successful admin proposal.
- `CmdEpochChecker::advance_apply()` integrates with apply advancement in the peer. Production calls remove pending epoch-changing commands once apply reaches their index, allowing later proposals that were blocked by those epoch changes to receive epoch mismatch feedback and retry.
- `Callback`, `ExtCallback`, and snapshot types integrate with raftstore's asynchronous command completion model. Tests use `engine_panic::PanicSnapshot` and `engine_test::kv::KvTestSnapshot` to avoid real storage snapshots.
- `TransferLeaderContext` depends on `bytes::Bytes`, `codec::NumberEncoder`/`NumberDecoder`, `BufferReader`, and `TransferLeaderCustomContext` from the coprocessor layer.
- `make_transfer_leader_response()` is adjacent to the transfer-leader context code and shares the same command-reply semantics, though the test chunk only validates context encoding.

## Risks And Edge Cases

- Admin command classification is brittle by design. If a new `AdminCmdType` is added, these enum-wide tests should fail until developers explicitly decide whether it requires sync-log and urgent handling.
- `get_sync_log_from_request()` and `ProposalContext::SYNC_LOG` are tied to raft-log durability behavior. Misclassifying an epoch-changing or topology-changing command as non-sync can expose durability or ordering bugs after crashes.
- `is_request_urgent()` gates follower lazy-commit behavior. Missing split/merge/conf-change style commands can increase availability windows where followers lag important region metadata changes.
- `ProposalContext::from_bytes()` truncates unknown bits for one-byte input but panics on multi-byte input. That is acceptable for current internal context bytes, but forward compatibility requires care if more than eight context flags are ever needed.
- The `test_entry_context()` combinations omit `ROLLBACK_MERGE` and empty context. Other tests or production coverage need to catch regressions in those branches.
- `RequestInspector::inspect()` allows only `Get`, `Snap`, and `ReadIndex` as read commands and a small set of write command types as write commands. New `CmdType` variants need explicit classification or they may be treated as errors.
- Mixed read/write batches are rejected. Any future batching feature that tries to mix reads and writes must alter this contract deliberately and update tests.
- Local reads require both current-term application and a valid lease. Weakening either condition can serve stale data after leader transfer or lease uncertainty.
- Stale-read flag precedence means stale reads bypass normal lease/read-index decisions. This is intentional but sensitive to header flag parsing with `WriteBatchFlags::from_bits_check()` and `from_bits_truncate()` in nearby transfer-leader handling.
- `ProposalQueue::push()` assumes strictly increasing `(term,index)` ordering. Tests cover ordered insertion only; production callers must never enqueue out-of-order proposals.
- `ProposalQueue::find_proposal()` panics if it finds a proposal in the searched term with a different index before the requested index. That panic protects an invariant but could take down a peer if proposal queue ordering or raft apply sequencing is corrupted.
- `test_uncommitted_proposals()` specifically guards committed-callback misuse across term changes. A regression here can cause client-visible success callbacks for commands that were never committed.
- `CmdEpochChecker` assumes its deque remains small because `admin_cmd_epoch_lookup()` groups epoch-changing command conflicts into version and conf-version dimensions. Adding a new epoch-changing admin class can alter this assumption.
- `CmdEpochChecker::maybe_update_term()` asserts terms never decrease. Any caller that invokes it with stale term data can panic.
- Attached callbacks must always be completed: on conflicting admin apply, term advance, or checker drop. Leaking them can hang clients waiting behind split/change-peer/merge proposals.
- `Drop` behavior differs during process shutdown: callbacks may be cleared without stale notification when `thread_group::is_shutdown(!cfg!(test))` reports shutdown. Tests run under `cfg(test)` and validate the non-shutdown path.
- `TransferLeaderContext::from_bytes()` treats an unknown tag as an error and parses custom payloads until input is exhausted. Malformed varint lengths or truncated key/value bytes propagate decode errors; tests cover only well-formed inputs.
- `TransferLeaderContext::get_custom_ctx()` returns the first matching key. Duplicate custom keys are not rejected, so coprocessor producers should avoid ambiguous duplicate entries.

## Test Signals

- The chunk itself is a set of unit test signals. Running the `raftstore` crate tests for `store::peer::tests` should exercise all functions in this range without requiring a multi-node TiKV cluster.
- Adding any `AdminCmdType` should cause `test_sync_log()` and `test_urgent()` to force an explicit classification update.
- Proposal context regressions should appear as failures in `test_entry_context()` when `to_vec()`/`from_bytes()` lose expected bits or change the single-byte representation.
- Request routing regressions should appear in `test_request_inspector()` for admin proposal type, stale read, read quorum, lease-valid local reads, applied-term gating, invalid command types, and mixed read/write batches.
- Proposal queue regressions should appear in `test_propose_queue_find_proposal()` as missing propose times, unexpected retained proposals after lookup, or failed removal of front proposals.
- Callback lifecycle regressions should appear in `test_uncommitted_proposals()` as panics from a committed callback not invoked when it should be, or from an uncommitted callback invoked incorrectly.
- Epoch conflict regressions should appear in `test_cmd_epoch_checker()` as wrong conflict indexes, stale pending commands after apply, failure to clear on term advance, or callbacks not delivered on apply/drop/term-change paths.
- Transfer-leader wire-format regressions should appear in `test_transfer_leader_context()` as failed round trips for empty, command-reply, or custom key/value contexts.
- Additional useful coverage would include `ProposalContext::ROLLBACK_MERGE`, invalid multi-byte proposal contexts, malformed `TransferLeaderContext` payloads, duplicate custom context keys, replica-read policy, and transfer-leader admin requests carrying `TRANSFER_LEADER_PROPOSAL`.
