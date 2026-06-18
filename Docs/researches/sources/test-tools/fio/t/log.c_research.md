# sources/test-tools/fio/t/log.c

## Purpose
Minimal `log_err()` and `log_info()` implementation for standalone test tools that link fio helper libraries.

## Important APIs, Types, and Functions
Defines `log_err(const char *format, ...)` and `log_info(const char *format, ...)`. Both format into a fixed 1024-byte stack buffer with `vsnprintf()`, clamp the length with fio's `min()`, and write to `stderr` or `stdout`.

## Control Flow
Each call formats variadic input, clamps output to buffer capacity, then writes one item through `fwrite()`.

## State and Persistence Behavior
No persistent state; output goes to standard streams.

## Dependencies and Integration Points
Uses `../minmax.h` and satisfies logging references from small C utilities such as `gen-rand.c`.

## Risks
Return value is `fwrite()` item count rather than byte count, so callers expecting standard printf-like semantics may be surprised. Output longer than 1023 bytes is truncated.

## Test Signals
Compilation/linking of standalone utilities and visible stdout/stderr messages are the primary signals.
