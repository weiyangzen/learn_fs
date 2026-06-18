# sources/object-store/rustfs/crates/ecstore/src/cache_value/mod.rs

## Purpose
This module exposes cache-value submodules and a process-global cancellation token for raw list-path operations.

## Important APIs, Types, and Functions
- `pub mod metacache_set` exports the distributed listing implementation.
- `LIST_PATH_RAW_CANCEL_TOKEN: Arc<CancellationToken>` is initialized with `lazy_static`.

## Control Flow and State Behavior
There is no function control flow here. The cancellation token is allocated at first static access and can be cloned by callers that need a shared cancellation signal.

## Dependencies and Integration Points
Depends on `lazy_static`, `Arc`, and `tokio_util::sync::CancellationToken`. It is the module-level integration point for consumers of `metacache_set`.

## Persistence
No persistence. The token is process-local runtime state.

## Risks and Edge Cases
A single global cancellation token, once cancelled, remains cancelled. If used as a reusable global for multiple independent listings, cancellation could permanently affect future operations unless callers create child tokens or the process recreates state elsewhere.

## Test Signals
No inline tests in this file. Behavior is mostly covered indirectly by `metacache_set` tests.
