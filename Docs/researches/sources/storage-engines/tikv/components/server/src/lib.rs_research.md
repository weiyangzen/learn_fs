## sources/storage-engines/tikv/components/server/src/lib.rs

Purpose: crate root for the server component.

Important APIs/types/functions: enables specialization with `#![feature(specialization)]`, imports `tikv_util` macros, and exposes modules `setup`, `common`, `memory`, `raft_engine_switch`, `server`, `server2`, and `signal_handler`; `utils` remains private.

Control flow: no direct runtime flow; module export structure determines which server helpers are externally available.

State/persistence: none directly.

Dependencies/integration: downstream code imports this crate to run or compose TiKV server startup. Public modules expose both legacy/common startup utilities and newer server variants.

Risks: specialization requires nightly/compatible toolchain support; public module exposure increases API surface and coupling.

Test signals: tests live in submodules rather than the crate root.
