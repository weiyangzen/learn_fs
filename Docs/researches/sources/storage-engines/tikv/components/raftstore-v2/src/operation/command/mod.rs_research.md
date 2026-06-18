# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/mod.rs

## Purpose
Top-level replicated command pipeline for raftstore-v2. It validates proposals, appends raft entries, schedules committed entries to apply FSMs, applies normal/admin commands in order, flushes write batches, reports apply results, and drives peer-side state updates.

## Important APIs, Types, And Functions
`parse_at` decodes protobuf messages with panic-on-corruption diagnostics. `CommittedEntries` batches raft entries with proposal callbacks. `new_response` preserves request UUIDs. Peer methods include `schedule_apply_fsm`, `validate_command`, `propose`, `propose_with_ctx`, `post_propose_command`, `schedule_apply_committed_entries`, `on_apply_res`, and `post_propose_fail`. `ApplyFlowControl` and apply methods `apply_committed_entries`, `apply_entry`, `maybe_flush`, `flush`, and `apply_unsafe_write` form the apply worker core.

## Control Flow
Leaders validate store id, peer id, leadership, term, region epoch, force-leader state, and flashback state before proposing. Proposals are appended through raft and stored with callbacks and waterfall metrics. Committed raft entries are matched to proposal callbacks and sent to the apply FSM. Apply decodes simple-write batches first, otherwise decodes admin/conf-change requests, validates epochs and flashback state, dispatches to write/admin handlers, records admin results, and buffers callbacks. `flush` writes the tablet write batch with WAL disabled, updates flush state applied index in the write callback, reports `ApplyRes`, flushes observers, and then resolves client callbacks.

## State And Persistence Behavior
Raftstore-v2 relies on raft engine persistence before kv/tablet memtable flushes, so it does not persist commit index/term in kv apply state like v1. Data writes are staged in `write_batch` and flushed to tablet with applied index in `FlushState`. Apply results carry admin side effects, data CF modifications, metrics, bucket stats, and SST applied indexes back to peer FSM. Peer-side `on_apply_res` updates raft applied index/term, entry cache, proposal control, read progress, split flow control, storage stats, apply trace, and recovery state.

## Dependencies And Integration Points
Re-exports admin/write/control APIs and integrates with raft, raftstore proposal queues, apply pools, tablet registry/scheduler, read progress, coprocessor observers, PD bucket metadata, flashback checks, simple-write codec, conf-change modules, split/merge/flashback/admin handlers, and metrics.

## Risks And Edge Cases
Silent raft proposal drops are converted to `NotLeader`. Force-leader mode panics on ordinary proposals except rollback merge. Apply uses savepoints to roll back partial batch work on command errors. Corrupted entry payloads panic. Flow control yields by time or written bytes and can trigger manual flush when apply trace needs it. Callbacks are delayed until after apply results are reported so subsequent messages observe admin side effects.

## Test Signals
Local tests are in submodules, while this file exposes failpoints for apply handling and report skipping. Observable signals include proposal/apply histograms, write trackers, apply result side effects, admin result dispatch, callback ordering, and recovery/flush traces.
