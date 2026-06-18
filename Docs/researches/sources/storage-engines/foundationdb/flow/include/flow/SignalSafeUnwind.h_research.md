<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/SignalSafeUnwind.h -->
# sources/storage-engines/foundationdb/flow/include/flow/SignalSafeUnwind.h

Purpose: This header exposes a test-visible counter for signal-safe unwinding integration. It allows tests to observe interception of `dl_iterate_phdr` calls.

Important APIs and types: The only declaration is `extern int64_t dl_iterate_phdr_calls`, after including `flow/Platform.h`.

Control flow: No control flow is implemented in the header. The implementation increments or uses the counter when signal-safe unwinding intercepts `dl_iterate_phdr`.

State and persistence behavior: State is a process-local 64-bit counter. It is not persisted and is intended for tests/diagnostics.

Dependencies and integration points: It depends on platform definitions and the unwinding/crash-handling implementation. It relates to stack capture and signal-safe profiler or crash paths.

Risks: The counter is global and may be racy if read while unwinding occurs concurrently unless implementation uses atomic-like discipline. Exposing internals to tests can couple tests to implementation details.

Test signals: Tests should reset/read the counter around stack-unwind operations and verify expected interception counts without requiring exact values in highly platform-dependent paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/SignalSafeUnwind.h -->
