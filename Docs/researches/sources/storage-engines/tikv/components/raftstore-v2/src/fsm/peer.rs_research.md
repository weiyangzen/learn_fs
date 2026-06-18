# sources/storage-engines/tikv/components/raftstore-v2/src/fsm/peer.rs

Purpose: Implements the batch-system FSM wrapper for a single raft peer and the delegate that dispatches `PeerMsg` variants into peer/operation logic.

Important APIs/types/functions: `SenderFsmPair` pairs a loose bounded sender with a boxed `PeerFsm`. `PeerFsm` owns `raft::Peer`, an optional mailbox, receiver, tick registry, and stopped flag. `PeerFsm::new` creates the underlying peer and queue. `recv` drains queued `PeerMsg`s into a batch. `Fsm` impl wires mailbox ownership into batch-system. `PeerFsmDelegate` owns temporary mutable access to the FSM and `StoreContext`, with `schedule_tick`, `on_start`, `on_receive_command`, `on_tick`, and `on_msgs`.

Control flow: `on_start` optionally pauses for replay, schedules raft/split/PD/compact ticks, checks merge, starts apply FSM for initialized storage, generates buckets, and wakes leader ready handling. `on_msgs` matches every peer message: raft messages, read/write/admin commands, ticks, apply results, split/merge events, persistence callbacks, snapshot events, bucket refresh, compact log, unsafe recovery, capture changes, and test-only waits. After processing a batch it proposes pending writes, schedules pending ticks, and may acknowledge transfer-leader messages.

State and persistence behavior: The FSM itself stores tick registration and queue state. Persistent effects are delegated to `Peer` methods through raft proposals, state changes, apply scheduling, tablet cleanup, and raft-ready handling. Drop drains pending read/simple-write requests and responds with region-not-found errors to avoid hanging deterministic callbacks.

Dependencies and integration points: It integrates batch-system, raftstore transport/read callbacks, tracker metrics, `StoreContext`, operation modules, `ReplayWatch`, router messages, and the underlying raft peer/storage types.

Risks: `PeerTick::CheckPeerStaleState` and `PeerMsg::Noop` are unimplemented. Missing mailbox for a serving peer causes `slog_panic`. Tick registry correctness prevents duplicate scheduling; failure to clear it would stall ticks. The large message match is a high-change surface where adding new router messages must be reflected here.

Test signals: Assertions cover tick variant count. Integration tests should verify every major `PeerMsg` path, drop responses, tick scheduling, replay start, and leader command latency tracking.
