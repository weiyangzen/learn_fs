# sources/storage-engines/tikv/components/profiler/src/lib.rs

Purpose: Exposes the public profiling API and selects the backend implementation by platform and feature flag. The public surface is intentionally tiny: callers use `profiler::start(path)` and `profiler::stop()`.

Important APIs/types/functions: The file imports `tikv_alloc`, documents gperftools and Callgrind requirements, and conditionally compiles `profiler_unix` for `all(unix, feature = "profiling")`; otherwise it compiles `profiler_dummy`. It re-exports the selected module's functions so downstream code does not need cfg gates.

Control flow: There is no runtime control flow in this file. Compile-time cfg chooses one of two modules. Documentation explains that Callgrind requires `--instr-atstart=no`, while gperftools writes a profile file named by `start`.

State and persistence behavior: State is delegated to the selected backend. The dummy backend has no state; the Unix backend stores active profiler state in a mutex and may write profile artifacts.

Dependencies and integration points: `tikv_alloc` is externally referenced to keep allocator linkage. The crate is a developer tool used by examples or ad hoc profiling instrumentation without requiring production code to depend on backend details.

Risks: Because both backends export the same names, behavioral differences are feature-dependent: without profiling, `start` returns false and no profiling occurs. Callers that treat `false` as fatal need to account for default builds. Documentation drift from backend behavior would confuse profiling workflows.

Test signals: Compile-time cfg coverage is the main signal. The `prime` example exercises the public API with real profiling enabled.
