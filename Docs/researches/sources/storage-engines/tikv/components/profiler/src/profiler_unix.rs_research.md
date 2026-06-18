# sources/storage-engines/tikv/components/profiler/src/profiler_unix.rs

Purpose: Implements real profiling for Unix builds with the `profiling` feature, selecting Callgrind when running under Valgrind and gperftools otherwise.

Important APIs/types/functions: `Profiler` tracks `None`, `GPerfTools`, or `CallGrind`. `ACTIVE_PROFILER: Mutex<Profiler>` serializes profiling sessions. `start(name)` checks for an active session, detects Valgrind with `valgrind_request::running_on_valgrind`, starts Callgrind instrumentation or `gperftools::PROFILER`, records the active backend, and returns true. `stop()` stops the recorded backend and resets the state, or returns false if nothing is active.

Control flow: `start` locks global state and rejects nested profiling. Backend choice is runtime based. `stop` matches the stored backend so it calls the correct stop API; this avoids stopping gperftools after a Callgrind start or vice versa.

State and persistence behavior: Active state is process-global under a mutex. gperftools writes a profile file named by the caller. Callgrind emits through Valgrind. No TiKV engine state is affected.

Dependencies and integration points: It uses `lazy_static`, `gperftools`, `callgrind`, and `valgrind_request`, all enabled by the manifest feature. It is re-exported as the crate public API from `lib.rs`.

Risks: Backend start/stop calls use `unwrap()`, so native backend errors panic. The TODO notes weak multi-thread support; a single global session prevents overlap and may not isolate thread-specific work. Holding the mutex while starting/stopping backend calls could block other callers briefly.

Test signals: No unit tests. The `prime` example under normal execution and Callgrind execution is the intended validation path.
