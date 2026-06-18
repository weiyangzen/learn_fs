# sources/storage-engines/wiredtiger/test/suite/test_prefetch03.py

## Purpose
Verifies prefetch is incompatible with in-memory databases and logs a compatibility message instead of enabling it.

## APIs, Types, And Functions
Defines `test_prefetch03` with default and in-memory connection config scenarios. It uses `reopen_conn` and `expectedStdoutPattern` for the in-memory warning.

## Control Flow, State, And Persistence
The default scenario reopens the current home with prefetch available/default-on and verbose prefetch logging. The in-memory scenario reopens with `in_memory=true` plus the same prefetch settings and expects a stdout message saying the configuration is incompatible. No table state is created; the test is purely connection configuration behavior.

## Dependencies, Integration, Risks, And Test Signals
Depends on connection config handling and verbose prefetch messaging. Risks are enabling prefetch in in-memory mode or failing the open instead of disabling/logging. Signal is successful reopen plus expected warning for the in-memory path.
