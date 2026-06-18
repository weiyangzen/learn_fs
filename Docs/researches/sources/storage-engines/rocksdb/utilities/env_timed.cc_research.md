# sources/storage-engines/rocksdb/utilities/env_timed.cc

## Purpose
This file implements a timed filesystem/environment wrapper that records filesystem operation latency into RocksDB `PerfContext` counters.

## Important APIs, Types, and Functions
`TimedFileSystem` derives from `FileSystemWrapper` and overrides creation, metadata, delete/create/rename/link/lock, and logger methods. Each override wraps the forwarded call with the matching `PERF_TIMER_GUARD` counter. `NewTimedFileSystem` returns a shared timed wrapper. `NewTimedEnv` creates a `CompositeEnvWrapper` combining the base Env with a timed filesystem.

## Control Flow
Every overridden method starts the relevant PerfContext timer guard, calls the base `FileSystemWrapper` implementation, and returns its `IOStatus`. `NewTimedEnv` obtains the base env's filesystem, wraps it, and returns a newly allocated composite env.

## State and Persistence Behavior
The wrapper does not alter filesystem semantics or store its own counters. Timing accumulates in thread-local/global PerfContext fields according to RocksDB's perf-level settings.

## Dependencies and Integration Points
It depends on `env/composite_env_wrapper.h`, `monitoring/perf_context_imp.h`, Env/FileSystem APIs, and `rocksdb/status.h`. Consumers call public `NewTimedEnv` or `NewTimedFileSystem` to instrument filesystem calls.

## Risks and Edge Cases
Only methods overridden here get explicit timers; operations performed on returned file objects are not wrapped by this class unless separately instrumented. Timers record only when PerfContext is enabled at a suitable level. `NewTimedEnv` returns a raw pointer, so callers own deletion. The wrapper delegates all status behavior and does not add validation.

## Test Signals
`env_timed_test.cc` enables `PerfLevel::kEnableTime`, opens a writable file through `NewTimedEnv`, and asserts the corresponding counter becomes positive. Broader tests could cover each timer field.
