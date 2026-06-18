# sources/security-integrity/cryfs/crates/utils/src/async_drop/result.rs

Purpose: wraps `Result<AsyncDropGuard<T>, E>` so successful values are cleaned up and errors are no-op during async drop.

Important APIs/types/functions: `AsyncDropResult<T,E>` with `new`, `err`, `ok`, `as_inner`, and `into_inner`.

Control flow: `async_drop_impl` matches the inner result; `Ok` calls the guard cleanup, `Err` returns success.

State/persistence: stores the original result in memory. `into_inner` bypasses wrapper cleanup and transfers responsibility for an `Ok` guard.

Dependencies/integration: useful for APIs that need one guard-like value even when construction failed.

Risks: error variant cleanup is intentionally absent; any partially-created resources must already have been handled before wrapping. `ok()` returns `&T`, hiding guard identity.

Test signals: unit tests cover accessors, into-inner for both variants, ok cleanup, and err no-op cleanup.
