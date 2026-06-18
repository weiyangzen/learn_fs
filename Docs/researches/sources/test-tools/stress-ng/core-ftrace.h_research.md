# sources/test-tools/stress-ng/core-ftrace.h

## Purpose

This header exposes the optional ftrace lifecycle used by stress-ng: start tracing, stop and report, free collected data, and add a PID to the ftrace PID filter.

## Important APIs, Types, And Functions

It declares `stress_ftrace_start`, `stress_ftrace_stop`, `stress_ftrace_free`, and `stress_ftrace_add_pid`. No ftrace-specific structs are exposed; implementation details remain private to `core-ftrace.c`.

## Control Flow

Callers can treat the API as safe on all platforms. Unsupported builds provide stubs, so the normal lifecycle can be called unconditionally when ftrace options are enabled.

## State And Persistence Behavior

The header owns no state. The implementation maintains global ftrace collection state and may mutate kernel tracing controls while active.

## Dependencies And Integration Points

The declarations rely on `pid_t` availability through project includes. The API is integrated with command-line option handling and stress run start/stop hooks.

## Risks And Test Signals

The public contract should remain simple and stub-safe. Compile tests on unsupported platforms and runtime tests with and without `OPT_FLAGS_FTRACE` are the main signals.
