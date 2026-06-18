## sources/object-store/garage/src/api/common/lib.rs

Purpose: crate root for `garage_api_common`.

Important APIs/types/functions: imports tracing macros with `#[macro_use] extern crate tracing;` and publicly exposes `common_error`, `cors`, `encoding`, `generic_server`, `helpers`, `router_macros`, `signature`, and `xml`.

Control flow: module wiring only.

State/persistence: none.

Dependencies/integration: every API crate imports shared modules through this root. Public module layout is part of the workspace's internal API contract.

Risks: changing visibility or module names has broad compile-time impact across S3, K2V, and admin crates.

Test signals: no direct tests; compile-time module imports are the primary signal.
