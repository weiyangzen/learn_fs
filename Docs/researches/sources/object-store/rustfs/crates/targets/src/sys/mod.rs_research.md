## sources/object-store/rustfs/crates/targets/src/sys/mod.rs

Purpose: declares the `sys` module namespace for target system utilities.

Important APIs/types/functions: exposes `pub mod user_agent;`.

Control flow and state: none.

Dependencies and integration points: lets callers import `crate::sys::user_agent` and keeps system utility files under one module boundary.

Risks: no direct behavior. Any public API stability resides in child modules.

Test signals: none here; child module tests cover actual behavior.
