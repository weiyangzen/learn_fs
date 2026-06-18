# sources/storage-engines/tikv/components/test_raftstore/src/lib.rs

Purpose: this crate root exposes the legacy raftstore test harness. It declares the core modules, enables the `trait_alias` feature, imports `tikv_util` macros, and re-exports cluster, config, node, router, server, transport simulation, and utility APIs.

Important APIs, types, and functions: no local runtime functions are defined. The critical API is the public facade: `pub use crate::{cluster::*, config::Config, node::*, router::*, server::*, transport_simulate::*, util::*};`. This makes request builders, cluster constructors, filters, routers, and helpers available from the crate root.

Control flow: compile-time module declaration and re-export only. `cluster`, `config`, `node`, `router`, `server`, and `transport_simulate` are private modules with public items re-exported; `util` is public as a module as well.

State and persistence behavior: none directly. State is owned by the underlying cluster/node/server modules.

Dependencies and integration points: `#[macro_use] extern crate tikv_util;` makes macros such as `defer!`, `box_err!`, logging helpers, and safe panic utilities available to submodules in the older style used by this crate.

Risks and test signals: glob re-exports make this root sensitive to symbol collisions and API churn in submodules. Feature or macro import changes can break broad parts of the test harness even though this file has no runtime logic.
