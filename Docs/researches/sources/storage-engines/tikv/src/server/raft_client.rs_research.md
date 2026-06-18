# sources/storage-engines/tikv/src/server/raft_client.rs

Purpose: manages outbound raft transport streams to peer stores, including per-store queues, gRPC stream lifecycle, batching, snapshot side-channel scheduling, connection health inspection, pause/disconnect handling, and metrics.

Important APIs/types/functions: `MetadataSourceStoreId` formats/parses source-store metadata. `Queue` is the bounded stateful message queue. `Buffer`, `BatchMessageBuffer`, and `MessageBuffer` define batching behavior. `AsyncRaftSender` drains queues to gRPC and diverts snapshots. `StreamBackEnd` resolves/connects/retries streams. `ConnectionBuilder` packages dependencies. `RaftClient` exposes `send`, `flush`, allowlist, and health APIs. `HealthChecker` runs periodic gRPC health probes.

Control flow: `send` hashes region id to a raft connection, loads or starts a stream backend, pushes into the queue, and marks the queue dirty for later `flush`. `flush` wakes dirty queues. Backend `start` loops through backoff, store address resolution, channel connection, batch raft call, fallback to legacy raft RPC on unimplemented, and reconnect on disconnect. `AsyncRaftSender` fills buffers until full/empty, sends snapshots via snapshot scheduler, waits under heavy load when configured, and flushes to gRPC. Health checker watches stores in the connection pool and spawns per-store inspection loops.

State and persistence: all state is memory-only: global connection pool, per-client LRU queue cache, dirty/full lists, queues, channels, tombstone set, allowlist, health task handles, and latency map. Raft messages are not persisted here; raftstore is responsible for raft durability before transport.

Dependencies and integration: integrates with `StoreAddrResolver`, `SecurityManager`, gRPC `TikvClient`, snapshot scheduler, raft router extension callbacks, server config `VersionTrack`, load statistics, metrics, `health_controller`, and raftstore discard reasons.

Risks: queue full/paused/disconnected paths drop or reject transport sends and depend on callers handling `DiscardReason`. Address resolution or connection failures clear pending messages and report peers/store unreachable. Snapshot parsing unwraps snapshot data bytes. Health checker uses mutex-protected shared maps and must stop tasks on drop. Batch size is estimated, so config buffer margins matter for gRPC max message size.

Test signals: tests cover batch buffer fullness with context/extra context, config refresh impact on batch sizing, buffer push benchmark, and health checker creation/latency/start-stop management.
