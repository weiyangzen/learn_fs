# sources/storage-engines/rocksdb/utilities/env_timed_test.cc

## Purpose
This file is the smoke test for timed environment instrumentation.

## Important APIs, Types, and Functions
`TimedEnvTest.BasicTest` calls `SetPerfLevel(PerfLevel::kEnableTime)`, checks `get_perf_context()->env_new_writable_file_nanos`, constructs a memory env and wraps it with `NewTimedEnv`, then opens a writable file.

## Control Flow
The test begins with the writable-file timer at zero, performs one `NewWritableFile` through the timed environment, and expects the timer counter to be greater than zero.

## State and Persistence Behavior
The test uses an in-memory environment and only creates file `f` inside it. PerfContext timing state is the relevant mutable state.

## Dependencies and Integration Points
It depends on public Env and PerfContext APIs, the timed env factory, memory env implementation, and the test harness.

## Risks and Edge Cases
The test covers only one operation and assumes the timer has nonzero measurable duration. It does not reset PerfContext after the test or verify other timed methods.

## Test Signals
Passing indicates that `NewTimedEnv` routes filesystem creation through `TimedFileSystem` and that PerfContext timing counters are active when enabled.
