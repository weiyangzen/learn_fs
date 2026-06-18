# sources/user-network-fs/gcsfuse/tracing/span_names.go

Purpose: defines the canonical OpenTelemetry span-name vocabulary for gcsfuse FUSE, cache, prefetch, metadata, xattr, and write/upload flows. The file has no runtime control flow; its value is the shared contract between instrumentation call sites and trace consumers.

Important APIs/types/functions: exported string constants such as `FileCacheRead`, `LookUpInode`, `ReadDirPlus`, `CreateFile`, `WriteFileStreaming`, and `StreamingUploadFinalize`. Constants are grouped by operation class and are intended to be passed into the tracing handle in `trace_handle.go` and concrete tracers elsewhere in the package.

State/persistence: immutable compile-time constants only. No persistence or mutable state.

Dependencies/integration: package `tracing`; integrates with OpenTelemetry spans indirectly through `TraceHandle`. Risks are mostly naming drift, cardinality changes, and observability compatibility if callers hard-code names or dashboards depend on these exact strings. Test signals should come from tracing tests that assert emitted span names or from static usage searches that ensure each canonical operation uses a constant.
