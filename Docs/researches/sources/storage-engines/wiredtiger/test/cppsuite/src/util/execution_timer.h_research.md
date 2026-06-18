# sources/storage-engines/wiredtiger/test/cppsuite/src/util/execution_timer.h

## Purpose
Declares a timing helper for benchmark tests that wraps a callable, records elapsed nanoseconds, and emits metrics at destruction.

## Important APIs, Types, And Functions
`execution_timer(const std::string &id, const std::string &test_name)`, destructor, `append_stats`, and templated `track(T lambda)` are the main API. Private fields are `_id`, `_test_name`, and `_time_recordings`.

## Control Flow
`track` captures `steady_clock::now()` before and after the callable, stores elapsed nanoseconds, and returns the callable's integer return code so test code can apply normal WiredTiger checks.

## State And Persistence Behavior
Samples live in a vector until stats are appended. Persistence occurs through the metrics writer in the `.cpp`.

## Dependencies And Integration Points
Includes chrono/string/vector and `test.h`. Used by `api_timing_benchmarks.cpp` and bounded cursor perf tests.

## Risks And Test Signals
The timer measures the lambda and any surrounding capture overhead. Tests should keep lambdas minimal and should be aware that destructor timing controls metric emission.
