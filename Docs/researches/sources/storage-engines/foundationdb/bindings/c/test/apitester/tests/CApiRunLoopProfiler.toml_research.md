# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiRunLoopProfiler.toml

## Purpose
Exercises run-loop profiling under high-concurrency API correctness load.

## Important APIs, types, and functions
Sets `runLoopProfiler = true`, fixed 8 FDB threads, 8 databases, 16 client threads, 32 clients, one `ApiCorrectness` workload, and knob `run_loop_profiling_interval=0.001`.

## Control flow
The tester applies profiling network option and knob before setup, then runs the workload.

## State and persistence behavior
Persists normal correctness data and emits profiler-related client trace/log state.

## Dependencies and integration points
Connects TOML knob parsing, network option application, run-loop profiling internals, and API correctness workload.

## Risks and test signals
Parser compatibility for the compact knobs section matters. Success means profiler enablement does not destabilize workload execution.
