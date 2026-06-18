# sources/storage-engines/foundationdb/documentation/tutorial/print_in_order.actor.cpp

## Purpose
Flow solution to the Print in Order concurrency exercise. It starts three randomized actors but serializes output through promises.

## Important APIs, Types, and Functions
`print_msg_when_ready()` waits a random delay, waits for readiness, prints a message, and returns. `orchestrate()` creates three promises/futures, starts print actors, and signals each only after the previous one finishes. `main()` initializes Flow and runs `orchestrate()`.

## Control Flow
All print actors start immediately, but `orchestrate()` sends `p_first`, waits for first completion, sends `p_second`, waits, then sends `p_third`. Output is therefore deterministic despite random initial sleeps.

## State and Persistence Behavior
Only local promises, futures, delays, and messages are stored. No persistence.

## Dependencies and Integration Points
Uses Flow promises/futures/delay, deterministic randomness, platform/TLS initialization, and actor compiler support. Built as `print_in_order`.

## Risks
Sending promises in parallel makes output nondeterministic, as shown by comments. The small post-print delay is timing-sensitive but educational.

## Test Signals
Run repeatedly and assert output order is always `First`, `Second`, `Third`. Build validates actor syntax and Flow runtime setup.
