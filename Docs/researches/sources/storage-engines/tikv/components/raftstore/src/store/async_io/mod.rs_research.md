# sources/storage-engines/tikv/components/raftstore/src/store/async_io/mod.rs

Purpose: Declares the async I/O submodules for raftstore store workers.

Important APIs and types: It exposes `read`, `write`, and `write_router` modules. There are no local functions, types, or constants.

Control flow: None in this file. Runtime behavior lives in the three child modules.

State and persistence: None locally. The module boundary groups async raft-log fetching, snapshot generation, write batching, persistence, and write-worker routing.

Dependencies and integration points: Consumers import `store::async_io::read`, `store::async_io::write`, and `store::async_io::write_router` through this declaration.

Risks: The file is simple, but module visibility means removing or renaming any child module breaks raftstore async I/O wiring.

Test signals: No direct tests. Child modules provide their own tests, especially `write_tests.rs` and `write_router` tests.
