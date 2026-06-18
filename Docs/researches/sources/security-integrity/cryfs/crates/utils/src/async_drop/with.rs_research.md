# sources/security-integrity/cryfs/crates/utils/src/async_drop/with.rs

Purpose: helper macros/functions that run user work and then always call `async_drop` on a guard.

Important APIs/types/functions: exported macros `with_async_drop_2!` and `with_async_drop_2_infallible!`; function `with_async_drop(value, f)`.

Control flow: callbacks run first and their result is stored; cleanup runs afterward; cleanup errors are propagated or mapped before returning the callback result.

State/persistence: no storage beyond the owned guard. Cleanup side effects belong to the wrapped type.

Dependencies/integration: uses `AsyncDropGuard`, `AsyncDrop`, futures, and `lockable::InfallibleUnwrap` for infallible macro form.

Risks: if both callback and cleanup fail, cleanup error can mask callback result in some paths. TODOs question macro necessity and note friction for synchronous callbacks.

Test signals: tests cover success, callback error still dropping, macro success, and error mapping.
