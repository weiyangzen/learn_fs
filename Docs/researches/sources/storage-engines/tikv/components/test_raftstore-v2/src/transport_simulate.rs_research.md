# sources/storage-engines/tikv/components/test_raftstore-v2/src/transport_simulate.rs

Purpose: this file provides transport and router adapters that let raftstore-v2 tests inject message filters while still using the normal raftstore-v2 router and snapshot APIs.

Important APIs, types, and functions: `SimulateTransport<C>` wraps any channel/router-like object `C` plus an `Arc<RwLock<Vec<Box<dyn Filter>>>>`. It exposes `add_filter`, `clear_filters`, and `filters` for tests and higher-level wrappers. Its `Transport` implementation applies `test_raftstore::filter_send` before delegating `RaftMessage` delivery, while pass-through methods preserve allowlist, flush, and need-flush behavior. `SnapshotRouter<EK>` abstracts async snapshot acquisition and is implemented for both raw `RaftRouter<EK, ER>` and `SimulateTransport<C>`. `RaftStoreRouter` abstracts sending peer messages, raft messages, and snapshot status reports; it is implemented for raftstore-v2 `RaftRouter` and for the simulated wrapper.

Control flow: outbound transport sends enter the filter list first; if filters allow the message, the inner transport sends it. Snapshot calls bypass filters and delegate to the inner router snapshot method. Raft message delivery through `RaftStoreRouter` also applies filters in the `SimulateTransport<C>` implementation, which is how receive-side router wrappers simulate dropped or altered inbound messages.

State and persistence behavior: the only local state is the shared filter list. Snapshot persistence is not handled here; snapshot copy/report behavior is supplied by `node.rs` and server transport implementations.

Dependencies and integration points: it bridges legacy `test_raftstore::Filter` with raftstore-v2 `Transport`, `PeerMsg`, `RaftRouter`, and `RegionSnapshot` APIs. `handle_send_error` converts router send errors to raftstore results with region context.

Risks and test signals: filter ordering and shared ownership matter. Clones share the same filter list, so clearing filters on one clone affects all paths derived from it. Snapshot acquisition is not filtered, so tests simulating read/snapshot failures need to filter the underlying raft messages or use router behavior. `send_peer_msg` in the wrapper does not apply filters because filters are raft-message oriented; this distinction is important for tests that inject `PeerMsg` directly.
