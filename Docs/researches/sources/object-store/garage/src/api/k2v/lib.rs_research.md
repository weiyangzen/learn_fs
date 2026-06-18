## sources/object-store/garage/src/api/k2v/lib.rs

Purpose: crate root for K2V API module wiring.

Important APIs/types/functions: public `api_server`; private `error`, `router`, `batch`, `index`, `item`, and `range` modules. Imports tracing macros with `#[macro_use] extern crate tracing;`.

Control flow: module declaration only.

State/persistence: none.

Dependencies/integration: establishes which pieces are public to other crates. Only server entry point is exported; route/error internals remain crate-private.

Risks: changing module visibility affects embedding of K2V server in Garage daemon.

Test signals: compile-time module wiring.
