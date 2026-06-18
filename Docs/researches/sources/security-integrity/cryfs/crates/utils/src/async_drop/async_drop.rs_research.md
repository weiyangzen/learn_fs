# sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop.rs

Purpose: defines the core `AsyncDrop` trait for types that need fallible asynchronous cleanup.

Important APIs/types/functions: `#[async_trait] pub trait AsyncDrop { type Error: Debug; async fn async_drop_impl(&mut self) -> Result<(), Self::Error>; }`.

Control flow: implementors put cleanup in `async_drop_impl`; wrappers such as `AsyncDropGuard`, `AsyncDropArc`, maps, and mutex adapters call it.

State/persistence: no storage in this trait. Cleanup semantics depend on implementors and may release filesystem, network, or task resources.

Dependencies/integration: uses `async_trait` and `Debug`. Re-exported by `async_drop/mod.rs`.

Risks: Rust has no native async destructor, so correctness depends on wrappers enforcing explicit calls. Implementor errors propagate through guard APIs.

Test signals: behavior is indirectly tested by all async-drop wrapper tests.
