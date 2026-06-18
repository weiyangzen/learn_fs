<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Trace.h -->
# sources/storage-engines/foundationdb/flow/include/flow/Trace.h

Purpose: This header defines FoundationDB's structured trace-event API, severity model, trace batching helpers, audited-event whitelist, latest-event cache, trace file controls, and trace-to-metric integration hooks.

Important APIs and types: Key types include `Severity`, `ErrorKind`, `TraceEventFields`, `TraceBatch`, `SpecialTraceMetricType`, `AuditedEvent`, `BaseTraceEvent`, `TraceEvent`, `TraceInterval`, `LatestEventCache`, and `EventCacheHolder`. Public functions include `openTraceFile`, `closeTraceFile`, `traceFileIsOpen`, `flushTraceFileVoid`, formatter and clock-source selectors, trace role/group/universal-field setters, local-address controls, `disposeTraceFileWriter`, `getTraceFormatExtension`, `getTraceThreadId`, and `pingTraceLogWriterThread`.

Control flow: `TraceEvent` construction selects enabled/disabled/forced state by severity and audited-event rules. Chained `detail` calls convert values through `Traceable`, add metric fields, and append serialized string fields. Suppression and sampling must be called first on `TraceEvent`. `BaseTraceEvent` writes on explicit `log()` or destructor unless disabled. Latest-event tracking stores selected event fields by address and key.

State and persistence behavior: Trace fields are in-memory until written to trace files. `openTraceFile` configures rolling logs with default sizes; formatter/clock source selection must occur before opening. Static event counts track severity buckets. `g_trace_clock`, `g_traceBatch`, and `latestEventCache` are process-global trace state. Trace output is persistent log data.

Dependencies and integration points: It depends on Flow random, error, trace interfaces, `Traceable`, optional network addresses, and dynamic event metrics from `TDMetric`. It is used across the codebase for diagnostics, audit logging, metrics, buggify batches, crash investigation, and latest-error reporting.

Risks: Trace detail values can be truncated or suppress events based on size limits. Audited events bypass some suppression only if created through the literal whitelist path. Trace destructors have side effects, so move/disable semantics matter. Latest error tracking only records from the main thread. Formatter and clock source changes are unsafe after opening trace files.

Test signals: Tests should cover severity enablement/counts, detail conversion for primitive/string/enum values, suppression and sampling, audited event whitelist compile-time path, trace field parsing helpers, file open/roll/flush/close, latest-event cache, formatter and clock validation, error-kind fields, and trace-to-metric field typing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Trace.h -->
