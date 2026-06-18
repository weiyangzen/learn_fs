# Research: sources/storage-engines/tikv/components/test_storage/src/assert_storage.rs

## sources/storage-engines/tikv/components/test_storage/src/assert_storage.rs

Purpose: high-level assertion wrapper around `SyncTestStorage` for MVCC, raw KV, Raft-backed storage, locks, scans, GC, and error-shape validation. `AssertionStorage<E, F>` carries a synchronous store plus request `Context`; aliases specialize API v1.

Important APIs include constructors for plain Rocks and Raft storage, cluster leader refresh through `update_with_key_byte`, two-phase write/delete helpers with retry on not-leader/stale-command, get/batch/scan assertion methods, prewrite conflict/lock checks, commit/cleanup/rollback/resolve-lock/GC/delete-range helpers, raw KV CRUD/scan/batch/atomic/checksum assertions, and reusable GC test scenarios.

Control flow wraps storage calls, converts raw byte keys into `txn_types::Key`, and asserts either exact values or specific error variants. Raft-backed helpers retry a small number of times, inspect nested storage/txn/mvcc errors for region leadership failures, update context/engine to the current leader, then retry. State is the mutable `ctx` and `store` reference for raft tests; data persistence is in the underlying engine and raft cluster.

Dependencies include `test_raftstore`, `tikv::storage`, `kvproto`, `txn_types`, `api_version`, and `tikv_util` locks. Risks include fragile pattern matching on boxed error internals, retry count of three, assumptions about leader lookup by key, and panic-heavy test behavior. Test signals are explicit assertion helpers for success, error, invalid TSO, write conflict, lock contents, raw atomic compare-and-swap, checksum, and GC outcomes.
