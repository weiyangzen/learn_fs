<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/tracing_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/wrappers/tracing_test.go

Purpose: focused unit test for the tracing wrapper's span creation behavior.

Important APIs/types/functions: helper `newInMemoryExporter`; test double `dummyFS` implementing all `fuseutil.FileSystem` methods; test `TestSpanCreation`.

Control flow: installs an in-memory OTEL exporter, constructs `tracedFS` around `dummyFS` with `tracing.NewOTELTracer`, calls `StatFS`, then asserts one exported span named `fs.stat_fs` with `trace.SpanKindServer`.

State and persistence behavior: span export state is held in memory and reset during cleanup. Dummy filesystem performs no state changes.

Dependencies and integration points: OpenTelemetry SDK trace provider/exporter, gcsfuse OTEL tracer, and the traced wrapper.

Risks: only `StatFS` is tested here; broader operation mapping is covered by `internal/fs/tracing_test.go`. Global OTEL tracer provider changes can affect tests if cleanup is incomplete.

Test signals: confirms wrapper starts server spans and uses the expected operation name for `StatFS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/tracing_test.go -->
