# sources/security-integrity/cryfs/crates/utils/src/async_drop/sync_drop.rs

Purpose: synchronous adapter that calls `async_drop` from `Drop`, mainly for test convenience.

Important APIs/types/functions: `SyncDrop<T>(Option<AsyncDropGuard<T>>)` with `new`, `into_inner_dont_drop`, `inner`, `Deref`, and `DerefMut`.

Control flow: on drop, if a guard remains, it blocks on `async_drop`. Inside a multi-threaded Tokio runtime it uses `block_in_place` plus `Handle::block_on`; otherwise it uses `futures::executor::block_on`.

State/persistence: owns one optional guard. `into_inner_dont_drop` transfers cleanup responsibility.

Dependencies/integration: adapts async-drop resources to synchronous tests or scopes.

Risks: documented deadlock risk if cleanup needs tasks that cannot progress. `unwrap()` on cleanup errors panics in `Drop`.

Test signals: unit tests cover deref, mutation, inner access, into-inner transfer, runtime drop, and non-runtime drop.
