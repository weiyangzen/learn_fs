# sources/storage-engines/tikv/components/test_raftstore-v2/src/lib.rs

Purpose: this crate root exposes the raftstore-v2 test harness as a single import surface. It enables unstable Rust features needed by the crate, declares private modules for cluster, node, server, and transport simulation, makes `util` public, and publicly re-exports all module exports.

Important APIs, types, and functions: there are no local functions or types. The important behavior is export shaping: `pub use crate::{cluster::*, node::*, server::*, transport_simulate::*, util::*};` lets integration tests import constructors such as `new_node_cluster`, `new_server_cluster`, `Cluster`, `Simulator`, `SimulateTransport`, and utility helpers from `test_raftstore_v2` without module-qualified paths.

Control flow: compile-time module loading only. `cluster`, `node`, `server`, and `transport_simulate` are private modules but their public items are re-exported; `util` is also a public module for callers that want its namespace.

State and persistence behavior: none directly. All persistent test state is owned by the modules this root exposes.

Dependencies and integration points: `#![allow(incomplete_features)]` and `#![feature(type_alias_impl_trait)]` allow the crate to use unstable type-alias impl trait patterns in the v2 harness. The root integrates with TiKV's internal test crates by acting as the facade consumed by raftstore-v2 integration tests.

Risks and test signals: because this is a glob re-export facade, adding public names in submodules can change the crate API or create name ambiguity for downstream tests. Any compile failure here is usually caused by renamed module symbols or removed unstable feature needs rather than runtime logic.
