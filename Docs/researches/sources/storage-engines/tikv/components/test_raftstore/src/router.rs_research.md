# sources/storage-engines/tikv/components/test_raftstore/src/router.rs

Purpose: this file defines `MockRaftStoreRouter`, a minimal region-scoped router for tests that need to observe peer messages without running a full raftstore.

Important APIs, types, and functions: `MockRaftStoreRouter` stores a `HashMap<u64, LooseBoundedSender<PeerMsg<RocksEngine>>>` behind `Arc<Mutex<_>>`. `new()` creates an empty router. `add_region(region_id, cap)` creates a loose-bounded channel for a region, registers its sender, and returns the receiver to the test. It implements `CasualRouter<RocksEngine>` by wrapping `CasualMessage` in `PeerMsg::CasualMessage` and `try_send`ing it. It implements `SignificantRouter<RocksEngine>` by wrapping `SignificantMsg` in `PeerMsg::SignificantMsg` and force-sending it.

Control flow: tests register a region, exercise code that sends casual or significant messages, then read the returned receiver to assert message content/order. If a region is not registered, send methods return `RegionNotFound` through raftstore error types and log significant-send failures.

State and persistence behavior: no persisted state. The only state is the in-memory map of region senders.

Dependencies and integration points: it implements selected raftstore router traits for `RocksEngine`/`RocksSnapshot`, making it usable anywhere a casual or significant router is sufficient. `StoreRouter`, `ProposalRouter`, and `RaftStoreRouter::send_raft_msg` are present but unimplemented, explicitly limiting the mock's scope.

Risks and test signals: this mock is intentionally partial. Code paths that send store messages, proposals, or raft messages will panic if routed through it. It is best suited for unit tests of casual/significant peer messages. Channel capacity and `try_send` behavior can be used to test backpressure/error handling, while `force_send` for significant messages bypasses normal capacity failure.
