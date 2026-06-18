<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/tracing.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/wrappers/tracing.go

Purpose: FUSE filesystem wrapper that creates a root OpenTelemetry server span for each filesystem operation and records operation errors on the span.

Important APIs/types/functions: type `tracedFS`; constructor `WithTracing`; `invokeWrapped`; per-operation delegators mapping to tracing constants such as `tracing.StatFS`, `tracing.LookUpInode`, `tracing.ReadFile`, and `tracing.SyncFS`.

Control flow: each method calls `invokeWrapped` with the operation name and a closure for the wrapped method. `invokeWrapped` starts a server span, defers span end, invokes the wrapped operation with the propagated context, and records any returned error.

State and persistence behavior: stateless wrapper except for trace export side effects through `tracing.TraceHandle`. It does not change filesystem state directly.

Dependencies and integration points: inserted by `fs.NewServer` only when tracing is enabled. Uses `wrappedCall` type from monitoring package, `jacobsa/fuse` operation structs, and gcsfuse tracing constants.

Risks: one delegator per FUSE op means new operations can be missed. Wrong span names break observability queries. If the trace handle is nil or non-thread-safe, every operation path can be affected.

Test signals: wrapper-level test checks a span is created for `StatFS`; fs-level tracing integration tests cover all operation names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/tracing.go -->
