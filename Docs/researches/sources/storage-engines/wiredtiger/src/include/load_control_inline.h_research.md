# sources/storage-engines/wiredtiger/src/include/load_control_inline.h

## Purpose
Provides inline predicates for deciding whether the connection is read- or write-overloaded according to `WT_CONNECTION_LOAD_CONTROL`.

## Important APIs, Types, And Functions
- `__wt_conn_load_control_read_overload(WT_SESSION_IMPL *)` returns true when load control is enabled and `read_load >= control_threshold`.
- `__wt_conn_load_control_write_overload(WT_SESSION_IMPL *)` does the same for `write_load`.

## Control Flow
Both functions fetch the connection load-control object through `S2C(session)`, test `WT_CONN_LOAD_CONTROL` with `F_ISSET`, atomically load the relevant `uint8_t` load counter with relaxed ordering, compare it against the threshold, and otherwise return false.

## State And Persistence Behavior
The functions read volatile connection runtime state only. They do not mutate state or persist anything. Relaxed atomics mean decisions may be approximate, which is acceptable for throttling/load shedding but not for exact accounting.

## Dependencies And Integration Points
Depends on `load_control.h`, `session.h` (`S2C`), flag macros from `misc.h`, and atomic functions supplied by the platform abstraction. Callers can use these predicates in front-door operation admission paths.

## Risks
Using relaxed loads can produce stale decisions under concurrency; the design assumes load control is heuristic. A low threshold can reject work aggressively, while a disabled flag must be respected even with high counters.

## Test Signals
Unit tests can directly set `control_threshold`, `read_load`, `write_load`, and flags on a synthetic connection. Integration tests should validate operation behavior under cache pressure and ensure disabled load control never reports overload.
