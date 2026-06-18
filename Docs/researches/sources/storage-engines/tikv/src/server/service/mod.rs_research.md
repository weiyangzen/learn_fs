# sources/storage-engines/tikv/src/server/service/mod.rs

## Purpose
`service/mod.rs` is the module boundary for TiKV server gRPC services. It wires submodules into a small public surface and defines the shared network-error logging macro used by service implementations.

## Important APIs, Types, and Functions
The module declares private `batch`, `debug`, and `kv` modules plus public `diagnostics`. Its `pub use` block exports `DebugService`, `DiagnosticsService`, `KvService`, `ResolvedTsDiagnosisCallback`, `DefaultGrpcMessageFilter`, `RaftGrpcMessageFilter`, batch-command request/response aliases, measured batch response helpers, `GrpcRequestDuration`, and the public flashback futures.

`log_net_error!` is exported with `#[macro_export]`. It evaluates an error expression once, logs gRPC transport errors at `info!`, and logs all other server errors at `debug!`, adding the caller-supplied structured fields plus `"err"`.

## Control Flow
There is no runtime control flow beyond macro expansion. Importers access service implementations through these re-exports rather than reaching into private modules. Call sites such as `kv.rs` use `log_net_error!` in async error handlers after failed sink sends or storage futures.

## State and Persistence Behavior
This file has no state and no persistence behavior. It only changes compile-time module visibility and generated logging code.

## Dependencies and Integration Points
It integrates the server service tree with the rest of TiKV by exposing stable type aliases and service names. `log_net_error!` depends on `$crate::server::Error::Grpc` to classify transport errors. The macro is available crate-wide because of `#[macro_export]`, while service modules remain mostly encapsulated.

## Risks and Edge Cases
Changing re-exports can break downstream modules that import `KvService`, flashback helpers, or batch-command aliases from `server::service`. Because `log_net_error!` matches only `server::Error::Grpc`, wrapped or converted gRPC errors may be logged at `debug!` instead of `info!`. The macro consumes the error expression into a local binding, so callers cannot reuse that expression afterward.

## Test Signals
There are no local tests. Compile-time use sites validate module visibility and macro availability. Runtime logging behavior is indirectly exercised by service tests and integration tests that trigger gRPC failures.
