# sources/storage-engines/tikv/components/raftstore/src/compacted_event_sender.rs

## Purpose
This file adapts RocksDB compaction-finished events into raftstore store-control messages. It is the raftstore v1 implementation of `engine_rocks::CompactedEventSender`.

## Important APIs, Types, and Functions
- `RaftRouterCompactedEventSender<EK, ER>` holds a `Mutex<RaftRouter<EK, ER>>`.
- Its `CompactedEventSender::send()` implementation wraps a `RocksCompactedEvent` in `StoreMsg::CompactedEvent` and sends it to the raftstore control router.

## Control Flow
When RocksDB emits a compaction event, the sender locks the router mutex, constructs the store message, and calls `send_control`. Failures are logged as warnings and otherwise ignored.

## State and Persistence Behavior
The file does not persist data. It forwards compaction metadata from the storage engine into raftstore, where later handlers can update region size/statistics or trigger follow-up work.

## Dependencies and Integration Points
It depends on `engine_rocks::{CompactedEventSender, RocksCompactedEvent}`, `engine_traits::{KvEngine, RaftEngine}`, raftstore `StoreMsg`, and the v1 `RaftRouter`. The `KvEngine` implementation must use `RocksCompactedEvent` as its compaction event type.

## Risks and Edge Cases
- The router is protected by a standard mutex; compaction callback paths must not introduce deadlocks by re-entering with the same lock.
- Dropped `send_control` failures mean compaction events can be lost during shutdown or router failure.
- The implementation is specific to Rocks compaction events and not generic over other engine event types.

## Test Signals
No direct tests are present. Indirect signals would be raftstore components receiving `StoreMsg::CompactedEvent` after RocksDB compaction.
