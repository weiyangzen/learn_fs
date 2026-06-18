# sources/storage-engines/tikv/src/coprocessor/interceptors/mod.rs

Purpose: module facade for coprocessor execution interceptors. It declares `concurrency_limiter` and `deadline`, then re-exports `limit_concurrency` and `check_deadline`.

Important API surface: consumers import from `coprocessor::interceptors::*` instead of depending on submodule paths. There is no runtime control flow, state, persistence, or tests in this file.

Dependencies and integration: used by `endpoint.rs` to apply deadline and concurrency wrappers around handler futures. Risk is limited to public API organization: renaming or changing exports breaks endpoint imports and any future interceptor users.
