# sources/test-tools/fio/engines/null.c

## Purpose
Implements fio's fake `null` engine and an optional external C++ `cpp_null` engine. It performs no real I/O and is used to test fio scheduling, queueing, issue-time accounting, and external engine ABI behavior.

## Important APIs, Types, And Functions
`struct null_data` stores queued `io_u` pointers, queued count, and event count. Shared helpers are `null_init()`, `null_queue()`, `null_commit()`, `null_getevents()`, `null_event()`, `null_open()`, and `null_cleanup()`. C wrappers register the built-in C engine, while the C++/external section wraps `null_data` in `NullData` and exposes `get_ioengine()`.

## Control Flow
`null_init` chooses synchronous mode when `iodepth == 1`; otherwise it allocates an `io_u` array and marks the engine as setting issue time. `queue` completes immediately for sync mode, returns busy if previous async events are waiting, or stores the `io_u` for later commit. `commit` stamps issue time for all queued requests, marks them submitted for built-in builds, moves queued count into event count, and resets queued count. `getevents` returns and clears events only when a nonzero minimum is requested. `event` indexes the stored `io_u` array.

## State And Persistence
There is no persistent storage effect. State is purely in-memory per thread and exists only to model fio engine behavior.

## Dependencies And Integration Points
Depends on fio core `ioengine_ops`, issue-time helpers, and external engine ABI definitions. It conditionally compiles alternate behavior under `__cplusplus` and `FIO_EXTERNAL_ENGINE`.

## Risks
The async path supports only one outstanding committed batch at a time because `queue` returns busy while `events` is nonzero. `null_getevents()` ignores `max` and timeout. Dynamic changes to `td->io_ops->flags` in init require `td_set_ioengine_flags()` to keep fio state coherent.

## Test Signals
Test `iodepth=1` synchronous completion, `iodepth>1` queue/commit/getevents/event flow, issue-time accounting, busy behavior before events are consumed, read/write/trim fake operations, built-in registration, and external C++ engine loading through `get_ioengine()`.
