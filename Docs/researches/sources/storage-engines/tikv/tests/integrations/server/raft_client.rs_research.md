# sources/storage-engines/tikv/tests/integrations/server/raft_client.rs

## Purpose
This integration test validates TiKV raft-client transport behavior around gRPC streaming, batching fallback, reconnects, PD-backed store resolution, store block/allow lists, and network-inspection latency bookkeeping. It uses a mock `Tikv` gRPC service to count received raft messages without starting a full TiKV cluster for the basic transport cases.

## Important APIs, Types, and Functions
`get_raft_client` builds a `RaftClient` from a `ConnectionBuilder`, `VersionTrack<Config>`, `SecurityManager`, resolver, router, lazy worker scheduler, and `ThreadLoadPool`. `MockKvForRaft` implements `Tikv::raft` and `Tikv::batch_raft`, counting individual messages and batch envelopes; when `allow_batch` is false, `batch_raft` returns `UNIMPLEMENTED` to exercise fallback. `create_mock_server`, `create_mock_server_on`, and `check_msg_count` provide local test infrastructure.

## Control Flow
The first tests establish a mock server, send `RaftMessage`s through `RaftClient::send`, call `flush`, and assert counter changes. Reconnect coverage shuts down the mock server, waits for router notification, queues more sends, restarts the server on the same port, and verifies later delivery. PD resolver tests add stores to the mock PD handler, then test tombstone block-listing and explicit allow-list filtering. Async tests start network inspection after creating store connections and query `get_max_latency` / `get_all_max_latencies`.

## State, Persistence, and Dependencies
State is mostly in-memory: atomic counters, worker queues, raft-client connection state, PD mock store records, and health-checker latency maps. Dependencies include `grpcio`, `kvproto`, `raftstore`, TiKV server connection builder/resolver types, failpoints, and Tokio for async latency tests. No on-disk persistence is intentional.

## Integration Points, Risks, and Test Signals
The tests exercise compatibility between single-message and batch raft RPCs, resolver reactions to tombstone stores, reconnect backoff, and health checker lifecycle. Risks include timing sensitivity from sleeps, fixed port ranges, and async inspection tests that may pass without proving recovery after final connection failure. Strong signals are exact message counts, discarded-send assertions, and latency map presence checks.
