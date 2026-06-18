# sources/object-store/rustfs/crates/lock/src/client/mod.rs

## Purpose
Defines the generic lock client trait abstraction and factory for constructing local lock clients.

## Important APIs, Types, And Functions
`LockClient` is an async trait requiring acquire, release, refresh, force release, status, stats, close, online, and local checks. It provides default batch acquire/release implementations using `join_all`. `ClientFactory::create_local` returns an `Arc<dyn LockClient>` backed by `LocalClient`.

## Control Flow
Batch methods fan out all requests concurrently and collect `Result<Vec<_>>`, short-circuiting if any individual operation returns an error. Remote client support is present only as commented stubs.

## State And Persistence
No state in this module. Trait implementors own lock state.

## Dependencies And Integration
Uses `async_trait`, `futures::future::join_all`, `Arc`, and crate lock DTOs. `DistributedLock` depends on this trait for quorum-based fan-out across local or future remote clients.

## Risks And Edge Cases
Default batch acquire can leave earlier successful locks held if a later request returns an error rather than a failure response; implementors with atomic batch semantics should override it. Remote support is not active.

## Test Signals
No direct tests. Trait behavior is exercised through mock clients in `distributed_lock.rs` tests and through `LocalClient`.
