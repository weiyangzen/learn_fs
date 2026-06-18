# `sources/storage-engines/tikv/components/raftstore/src/store/msg.rs`

## Purpose
This file defines raftstore's message and callback contracts. It is the shared vocabulary for client raft commands, read/write responses, peer ticks, store ticks, significant peer events, casual peer notifications, inspected raft network messages, and store-level control messages.

## Important APIs, Types, and Functions
- `ReadResponse<S>` and `WriteResponse` wrap raft command responses; reads may include a `RegionSnapshot` and transaction extra operation.
- `PeerClearMetaStat` records raft and KV metadata cleanup durations.
- `Callback<S>` represents no-op, read, write, and test callbacks. Write callbacks can include proposed and committed early callbacks plus `TimeTracker` entries.
- `ReadCallback`, `WriteCallback`, and `ErrorCallback` abstract callback completion/error paths; `Vec<C>` implementations fan out errors and write notifications.
- `PeerTick` enumerates periodic peer tasks and provides stable tags/all-tick ordering.
- `StoreTick` enumerates store-level periodic tasks and maps to `RaftEventDurationType`.
- `MergeResultKind`, `SignificantMsg`, `CampaignType`, and `CasualMessage<EK>` model high-level peer events ranging from snapshot status and merge results to unsafe recovery, split, bucket refresh, force compaction, snapshot applied, and in-memory-engine load triggers.
- `RaftCmdExtraOpts` and `RaftCommand<S>` wrap user raft command requests with callback, send time, deadline, and disk-full behavior.
- `InspectedRaftMessage` carries a raft network message plus precomputed heap size for memory accounting.
- `PeerMsg<EK>` is the per-region FSM mailbox message enum.
- `StoreMsg<EK>` is the singleton store FSM control mailbox message enum.

## Control Flow
Callbacks are invoked by consuming the callback object: read callbacks receive `ReadResponse`, write callbacks receive `WriteResponse` or raft response, and error callbacks reuse normal response delivery. Write callbacks can notify proposed/committed stages before final result, and can expose mutable tracker lists for write-stage timing.

Peer/store pollers use `discriminant` methods to build slow-log distributions in parallel with `strum` variant names. `PeerMsg::is_send_failure_ignorable` identifies the rare significant message that can fail to send without treating it as fatal. Debug implementations intentionally summarize large or callback-bearing messages to avoid expensive or unsafe formatting.

## State and Persistence Behavior
The file defines message state but performs no IO. Persistence semantics are encoded in message meaning: `PeerMsg::ApplyRes`, `PeerMsg::Persisted`, `SignificantMsg::RaftLogGcFlushed`, snapshot/merge/unsafe recovery variants, and `StoreMsg::UnsafeRecoveryCreatePeer` are consumed by other modules to advance durable raft/KV state. `RaftCommand` includes deadline and disk-full options that influence proposal handling.

## Dependencies and Integration Points
The definitions depend on `engine_traits`, `kvproto`, raft, resource-control metering, health-controller latency inspection, futures channels, tracker, region snapshots, apply task results, unsafe recovery syncers, snapshot backup requests, worker bucket types, and metrics labels. `fsm/store.rs`, peer FSMs, apply FSMs, workers, transport, snapshot backup, unsafe recovery, tests, and external request routers all use these types.

## Risks and Edge Cases
- `Callback::invoke_read` panics if called on a non-read callback; callers must keep request classification correct.
- `PeerMsg` size is performance-sensitive and locally tested.
- Discriminant values must remain aligned with slow-log distribution arrays and `EnumCount`; test-only `StoreMsg::Validate` must stay last.
- Some messages are explicitly lossy (`CasualMessage`) while others must not be lost (`ApplyRes`, `SignificantMsg`). Wrong send path selection can cause correctness bugs.
- `RaftCommand::new_ext` copies only known extra option fields, so adding fields to `RaftCmdExtraOpts` requires updating construction logic.
- Debug formatting must avoid exposing huge payloads or consuming callbacks.

## Test Signals
Local tests assert `PeerMsg<RocksEngine>` remains 32 bytes and validate `StoreMsg` discriminant/variant-name slow-log alignment for selected variants. Additional useful tests would cover callback fanout/error behavior, proposed/committed callback one-shot behavior, `PeerTick::VARIANT_COUNT` alignment, and new message variant discriminants.
