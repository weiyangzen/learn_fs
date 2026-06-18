# sources/storage-engines/tikv/components/raftstore-v2/src/lib.rs

Purpose: Defines the crate-level structure and public API for raftstore-v2, TiKV's multi-raft implementation built on batch-system FSMs and operation modules.

Important APIs/types/functions: The file documents the architecture: batch-system threads, FSMs in `fsm`, raft wrapping in `raft`, and operations in `operation`. It enables `box_into_inner`, declares private modules `batch`, `bootstrap`, `fsm`, `operation`, `raft`, and `worker`, plus public `router`. Public re-exports include `StoreRouter`, `StoreSystem`, `create_store_batch_system`, `Bootstrap`, `StoreMeta`, simple-write/state-storage helpers, raftstore `Error/Result/Config`, PD/tablet worker tasks, and `Storage`.

Control flow: There is no runtime control flow. It defines the dependency direction: fields independent of batch-system belong in the raft peer module, while FSM wrappers remain swappable.

State and persistence behavior: Persistence is delegated to operation and raft modules; this file only exposes the types that manipulate it.

Dependencies and integration points: External crates use this root to construct batch systems, bootstrap stores, send router messages, access state storage helpers, and integrate worker tasks. It reuses `raftstore` v1 types such as config and errors.

Risks: Public API exports are stability points for tests and integration. The architecture comments are important: violating the split between `fsm` peer wrappers and underlying raft peer state would make future concurrency changes harder.

Test signals: Compile-time public API coverage and integration tests. No local tests in this file.
