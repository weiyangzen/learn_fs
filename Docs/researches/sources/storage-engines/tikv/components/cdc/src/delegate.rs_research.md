# sources/storage-engines/tikv/components/cdc/src/delegate.rs

## Purpose

`delegate.rs` implements the per-region CDC delegate that turns observed raftstore apply commands and incremental-scan entries into `cdcpb` change events for one or more downstream subscriptions. It is also the region-local resolved-ts gate: it tracks in-flight locks, keeps per-downstream lock heaps for observed subranges, sends region errors, stops observation, and toggles transaction-layer old-value capture through the shared `TxnExtraOp`.

The file is the CDC boundary between raftstore observation (`CmdBatch`, `ObserveHandle`), client delivery (`Sink`, `CdcEvent`, `Conn`), transaction decoding (`txn_types::{Lock, WriteRef, TimeStamp}`), and resolved-ts advancement (`endpoint::Advance`).

## Important APIs, Types, And Functions

- `DownstreamId` is an atomically allocated unique identifier used to avoid ABA mistakes when deregistering a subscription.
- `DownstreamState` models subscription progress: `Uninitialized`, `Initializing`, `Normal`, and `Stopped`. `ready_for_change_events` allows scan and delta entries during initialization, while `ready_for_advancing_ts` only allows resolved-ts after the incremental scan has completed.
- `on_init_downstream` and `post_init_downstream` perform atomic state transitions used by `Endpoint::run(Task::InitDownstream)` and `Initializer` completion.
- `Downstream` holds request identity, connection identity, requested KV API (`TiDb`, `RawKv`, etc.), loop filtering, observed range, sink, state, scan cancellation flag, and per-downstream resolved-ts state (`lock_heap`, `advanced_to`). `sink_event` attaches the request ID and handles sink failures; `sink_error_event` marks scan truncation and force-sends protocol errors.
- `PendingLock`, `LockTracker`, and `MiniLock` are the resolver state. `LockTracker::Preparing` buffers lock deltas while the asynchronous snapshot lock scan is still building the initial resolver; `Prepared` stores the region plus a `BTreeMap<Key, MiniLock>`.
- `Delegate` owns `region_id`, the raftstore `ObserveHandle`, memory quota, lock tracker, downstream list, `txn_extra_op`, and failure/lag bookkeeping.
- `Delegate::subscribe`, `unsubscribe`, `stop`, `stop_observing`, `mark_failed`, and `txn_extra_op` manage downstream lifecycle and observation.
- `Delegate::init_lock_tracker`, `finish_scan_locks`, `push_lock`, `pop_lock`, and `finish_prepare_lock_tracker` manage lock resolver construction and live lock deltas.
- `Delegate::on_batch` processes raftstore `CmdBatch` values, routing normal write batches to `sink_data` and split/merge admin commands to protocol errors.
- `Delegate::on_min_ts` computes each downstream's resolved-ts based on current global/store min-ts and tracked locks, then fills `Advance` buckets according to connection feature gates.
- `Delegate::convert_to_grpc_events` converts incremental-scan `KvEntry` records into one or more `CdcEvent::Event` values capped by `CDC_EVENT_MAX_BYTES`.
- Decode helpers `decode_write`, `decode_lock`, `decode_rawkv`, and `decode_default` translate storage-layer write/lock/default/raw records into `cdcpb::EventRow`.
- `ObservedRange` keeps both encoded and raw key range forms and filters raw/encoded event rows for partial-region subscriptions.

## Control Flow

Registration creates a `Delegate` through `endpoint.rs`, subscribes a `Downstream`, and later initializes the lock tracker while `initializer.rs` performs snapshot capture and incremental scan. During initialization, raftstore apply events may arrive first; `sink_txn_put` buffers lock additions/removals into `LockTracker::Preparing`. When the snapshot lock scan finishes, `finish_prepare_lock_tracker` overlays buffered deltas onto the snapshot lock set, accounts memory, and moves to `Prepared`.

Delta changes enter through `Delegate::on_batch`. Stale observe IDs are ignored. Each raft command checks response headers, then normal put requests are grouped by user key with `RowsBuilder`. RawKV puts are decoded directly. TxnKV write CF records produce commit/rollback rows and remove locks unless one-phase commit makes the commit row self-contained. Lock CF records produce prewrite rows, add locks, and mark that old value needs to be read. Default CF records attach the large value payload.

After rows are built, RawKV downstreams receive range-filtered raw rows. TiDB downstreams receive rows only if their state accepts change events, the key is inside their observed range, loop/import/DDL-source filtering permits the row, and old value is materialized if needed. If a downstream already has a resolved-ts lock heap, lock modifications are applied immediately so resolved-ts does not remain stuck on locks already committed or removed.

Resolved-ts advancement enters through `on_min_ts`. Delegates that are not `Prepared` increment `blocked_on_scan` and periodically warn. For each normal downstream, the first advance builds a per-downstream `lock_heap` from the shared region lock map filtered by `ObservedRange`. The downstream advances to `min(min_lock_ts, min_ts)`, never backwards. Depending on the connection feature gates, the result goes into multiplexed, exclusive batch, or compatibility resolved-ts output.

Administrative split and merge commands deliberately become epoch errors through `sink_admin`, which causes endpoint-level deregistration and client resubscription to the new region layout.

## State And Persistence Behavior

The delegate is in-memory only. Its durable source of truth is TiKV storage and raftstore apply order; this file does not write persistent CDC state. Important in-memory state includes:

- Shared per-region lock tracker, with memory quota accounting for key heap sizes and `CDC_PENDING_BYTES_GAUGE`.
- Per-downstream atomic state and scan cancellation flag.
- Per-downstream resolved-ts lock heap and `advanced_to`.
- `txn_extra_op`, a shared atomic flag read by the transaction layer. It is set to `ReadOldValue` when at least one downstream is attached and reset to `Noop` when observing stops.
- `ObserveHandle`, which can stop raftstore observation.

`Drop` returns memory held by pending/prepared lock tracking but intentionally does not update `txn_extra_op`; explicit lifecycle paths call `stop_observing` for that.

## Dependencies And Integration Points

- `raftstore::coprocessor::{CmdBatch, Cmd, ObserveHandle}` supplies observed apply events and observer handles.
- `endpoint::Advance` receives resolved-ts results; `Endpoint` owns scheduling and connection maps.
- `initializer::KvEntry` supplies incremental-scan entries for conversion into CDC events.
- `old_value::{OldValueCache, OldValueCallback}` is invoked for old values on delta prewrite/commit paths.
- `channel::{Sink, CdcEvent, SendError, CDC_EVENT_MAX_BYTES}` provides sink delivery and size splitting.
- `service::{Conn, FeatureGate, RequestId}` determines resolved-ts protocol shape.
- `txn_source::TxnSource` filters loopback CDC writes, Lightning physical imports, and lossy DDL reorg writes.
- `api_version::ApiV2` handles RawKV key/value timestamp encoding.
- `MemoryQuota` and CDC metrics provide backpressure and observability.

## Risks And Edge Cases

- Lock tracker memory accounting is subtle: preparing-state deltas allocate memory for buffered operations, then must be freed before prepared locks are charged. Incorrect accounting can either leak quota or allow unbounded pending locks.
- The shared region lock map is filtered into per-downstream heaps only once, then maintained by live lock deltas. Missing a `LockModifiedCount` update can permanently block resolved-ts.
- `decode_write` treats apply-time GC-fence rewrites specially by emitting an overlapped rollback. Any future write rewrite case must preserve CDC semantics here.
- Range filtering mixes encoded keys for TxnKV and raw keys for event rows. Wrong range form would leak or drop rows for observed subranges.
- Event size splitting uses row payload sizes, not full protobuf serialization size, so `CDC_EVENT_MAX_BYTES` is approximate.
- Some decoding paths use `unwrap`/`assert` on invariants supplied by TiKV storage encoding. Corrupt or unexpected records would panic rather than surface a CDC error.
- `sink_error_event` sets `scan_truncated` before force-sending the error; callers rely on this to stop concurrent incremental-scan delivery.
- `DownstreamState::Initializing` accepts change events but rejects resolved-ts. Reordering barriers in endpoint/initializer would break the guarantee that resolved-ts follows the complete incremental scan.

## Test Signals

The file has targeted unit coverage for protocol error mapping, delegate subscribe/unsubscribe behavior, observed range coverage and filtering, CDC loop/import/DDL source filtering, RawKV decoding including delete and expire timestamp, and lock tracker quota/delta behavior. Tests also cover admin split/batch-split/merge error conversion. These tests are strong for local delegate invariants but do not replace integration tests for raftstore apply ordering, sink backpressure under load, or multi-region resolved-ts behavior.
