<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Profiler.h -->
# sources/storage-engines/foundationdb/flow/include/flow/Profiler.h

Purpose: This header exposes Flow's run-loop profiling controls. It provides the public entry points to start and stop sampling/profiling against an `INetwork` instance.

Important APIs and types: `startProfiling(INetwork* network, Optional<int> period = {}, Optional<StringRef> outputFile = {})` starts profiling with optional sampling period and output path. `stopProfiling()` stops the profiler. `INetwork` is forward-declared and `Optional`/`StringRef` come from Flow headers.

Control flow: The header only declares controls; implementation wires profiling into the network/run-loop profiler. The optional period and output file determine sampling cadence and destination when provided.

State and persistence behavior: Runtime state is profiler activation and output state in the implementation. Persistence can occur through the output file parameter. There is no durable state in the header.

Dependencies and integration points: It depends on `flow/flow.h` and `Arena.h`, and complements `Platform.h` profiling hooks such as `setupRunLoopProfiler`, `stopRunLoopProfiler`, and `setProfilingEnabled`.

Risks: Profiling affects timing-sensitive code and may add signal or sampling overhead. Starting with a null or wrong network instance should be guarded by implementation. Output file paths can introduce filesystem failures.

Test signals: Smoke tests should start and stop profiling on a test network, verify optional period parsing, ensure output files are created when requested, and confirm repeated start/stop calls do not leak profiler state.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Profiler.h -->
