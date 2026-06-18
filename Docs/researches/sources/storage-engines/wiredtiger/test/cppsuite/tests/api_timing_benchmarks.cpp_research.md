# sources/storage-engines/wiredtiger/test/cppsuite/tests/api_timing_benchmarks.cpp

## Purpose
Defines a timing benchmark for frequently called WiredTiger session APIs.

## Important APIs, Types, And Functions
`class api_timing_benchmarks : public test` overrides `custom_operation` and uses `execution_timer` for begin transaction, commit transaction, rollback transaction, timestamp transaction uint, cursor reset, and cursor search. `_LOOP_COUNTER` is 1000.

## Control Flow
The constructor initializes operation tracking. The custom operation asserts one collection, opens a cursor, then times begin/commit with real inserts for `_LOOP_COUNTER / 10` iterations. It times rollback in a larger loop, then times many `timestamp_transaction_uint` calls inside one transaction and rolls it back.

## State And Persistence Behavior
The benchmark inserts additional keys during commit timing and uses the operation tracker through `thread_worker::insert`. Timings are persisted as 90th percentile metrics by `execution_timer` destructors.

## Dependencies And Integration Points
Depends on `execution_timer`, `instruction_counter` include presence, constants/logger, and the base `test` harness. It relies on pre-populated collection state and timestamp manager availability.

## Risks And Test Signals
The file creates timers for cursor reset/search but does not use them in the shown implementation, so no cursor timing metric is emitted unless future code adds samples. Timing includes lambda overhead and any transaction side effects. Successful signals are completed loops and perf stats from populated timers.
