# sources/storage-engines/wiredtiger/test/cppsuite/src/util/instruction_counter.h

## Purpose
Declares a benchmark helper that measures hardware instruction counts for a callable using Linux `perf_event_open`.

## Important APIs, Types, And Functions
`instruction_counter` exposes constructor, destructor, `append_stats`, and templated `track(T lambda)`. Private state includes metric id/test name, last instruction count, and `perf_event_attr`.

## Control Flow
`track` opens a perf event for the calling thread, resets and enables it, invokes the lambda, disables the counter, reads the count, stores it, closes the fd, and returns the lambda return code.

## State And Persistence Behavior
No database state is changed by the counter itself. Metrics persist via `append_stats` in the `.cpp`.

## Dependencies And Integration Points
Includes Linux perf/syscall/ioctl/unistd headers and `test.h` for test utilities. Used by instruction-count benchmark tests around low-level WiredTiger API calls.

## Risks And Test Signals
The helper is Linux-specific and permission-sensitive. It asserts `fd != -1` and exact read size. It does not aggregate multiple samples; later `track` calls overwrite `_instruction_count`.
