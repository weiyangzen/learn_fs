# Research: sources/storage-engines/tikv/components/test_raftstore/src/transport_simulate.rs

## sources/storage-engines/tikv/components/test_raftstore/src/transport_simulate.rs

Purpose: provides a programmable network/raft message simulation layer for raftstore tests. `Filter` exposes `before` and `after` hooks over `Vec<RaftMessage>`, while `SimulateTransport<C>` wraps any transport/router and applies shared `RwLock`-protected filters before forwarding messages. It implements `Transport`, `StoreRouter`, `ProposalRouter`, `CasualRouter`, `SignificantRouter`, `RaftStoreRouter`, and `LocalReadRouter`.

Important filters model packet loss, partitions, isolation, region-specific drops, snapshots, delayed/duplicated snapshots, random latency, lease-read context capture/removal, and arbitrary message retain predicates. `filter_send` is the central control path: run `before` filters in order until failure, send retained messages, then run matching `after` hooks in reverse order. Factories generate per-node filters for partitions and isolation.

State is in atomics and mutexes: notification counters, block booleans or allow counts, dropped message buffers, pending snapshot maps, delayed message queues, and captured lease read contexts. There is no persistence; behavior is intentionally transient test state. Dependencies include raftstore router traits, Rocks engine snapshots, raft message protobufs, crossbeam channel errors, and `tikv_util::Either`.

Risks include nondeterminism from random drop/latency filters, `unwrap` in snapshot capture/leading filters when expected sequencing is violated, lock contention inside filters, and inverted semantics of `RegionPacketFilter::when` where false means drop. Test signals are indirect: these filters are meant to be attached by raftstore tests to force elections, snapshot races, lease-read behavior, and network partitions.
