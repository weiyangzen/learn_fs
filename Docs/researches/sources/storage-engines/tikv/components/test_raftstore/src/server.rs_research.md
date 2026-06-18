# Research: sources/storage-engines/tikv/components/test_raftstore/src/server.rs

## sources/storage-engines/tikv/components/test_raftstore/src/server.rs

Purpose: builds the TiKV test RaftStore server simulator around `ServerCluster`, giving integration tests a real gRPC server, Raft store, storage engine, coprocessor endpoint, import service, GC worker, lock manager, resolved-ts path, optional in-memory engine, and simulated network filters. Important types include `AddressMap`, `ServerMeta`, `ServerCluster`, `SimulateEngine`, and transport aliases over `SimulateTransport`. `AddressMap` implements `StoreAddrResolver` for deterministic in-process address lookup.

Control flow centers on `ServerCluster::run_node_impl`, dispatched by API version. It allocates or reuses snapshot directories and listen addresses, builds coprocessor hooks, optional hybrid in-memory observers, raft routers, `RaftKv`, read pools, GC/resolved-ts workers, resource metering, import/debug/deadlock services, snapshot manager, `MultiRaftServer`, gRPC `Server`, lock manager, split checking, and finally stores all handles in `metas`. State is held in maps keyed by node/store id: storages, routers, importers, health controllers, snapshot managers, concurrency managers, raft clients, causal providers, and temp dirs.

Integration points are `Simulator` trait methods for start/stop, async commands, local reads, raft messages, filters, and routers, plus cluster constructors and gRPC client helpers. Risks are lifecycle leaks, address reuse after restarts, bind retry assumptions, optional worker cleanup, and filter direction mistakes. Test signals are helper constructors, snapshot retrieval, forwarding check in `setup_cluster`, and panics/asserts around missing leaders and service startup.
