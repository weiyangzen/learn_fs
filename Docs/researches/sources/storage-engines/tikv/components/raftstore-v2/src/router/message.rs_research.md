# sources/storage-engines/tikv/components/raftstore-v2/src/router/message.rs

Purpose: this file defines the typed message vocabulary for raftstore-v2 peer and store routers, plus constructors for common raft requests.

Important APIs/types/functions: `PeerTick` and `StoreTick` enumerate periodic peer/store tasks and expose tag mappings. `RaftRequest<C>`, `SimpleWrite`, `UnsafeWrite`, and `CaptureChange` wrap routed work with timestamps/channels. `PeerMsg` covers raft messages, queries, writes, admin commands, ticks, apply results, snapshots, split/merge/GC/tablet operations, CDC capture, flush/test hooks, and unsafe recovery commands. `StoreMsg` covers store-level raft/control messages, latency inspection, and unsafe recovery report/create-peer. Helper constructors create query/admin/simple-write/split messages.

Control flow: routers enqueue these enums into peer or store FSMs. The batch FSM dispatches on variants and invokes operation modules. Constructors consistently allocate response channels and set send timestamps for latency tracking.

State and persistence: messages carry protobuf requests/responses, syncers, encoded simple writes, and metadata, but do not persist data themselves. Some variants such as `Persisted`, `DataFlushed`, and `SnapshotSent` communicate persistence completion back to peers.

Dependencies/integration: depends on kvproto raft/PD/import protobufs, raftstore fetched logs/snapshot results/simple-write binary, resource-control metering, health latency inspector, and response channel types.

Risks: `PeerMsg` is a central compatibility surface; missing dispatch for a new variant would drop behavior. Unsafe recovery variants carry syncers whose lifetime matters. `StoreMaybeTombstone` semantics are intentionally ambiguous because PD cannot distinguish tombstone from not-found stores.

Test signals: no local tests. Exhaustive matching in FSM dispatch and integration tests provide coverage.
