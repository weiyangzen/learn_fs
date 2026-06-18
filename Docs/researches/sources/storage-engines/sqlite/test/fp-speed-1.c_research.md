# sources/storage-engines/sqlite/test/fp-speed-1.c

## Purpose
`fp-speed-1.c` benchmarks binary-to-decimal floating-point formatting speed by comparing C library `sprintf("%.17g")` with SQLite's `sqlite3_snprintf()` over a fixed array of representative `double` values.

## Important APIs, Types, and Functions
- Test data: static `double aVal[]` contains values across large, small, positive, negative, and subnormal-like exponent ranges.
- `timeOfDay()` provides microsecond wall-clock timing using Windows precise file time, SQLite VFS time on older Windows, or `gettimeofday()` elsewhere.
- `main()` parses an iteration count, runs formatting loops, prints ns/call and total seconds, and reports the relative speed ratio.

## Control Flow
The program requires `COUNT >= 100`. It times a loop calling `sprintf()` into a stack buffer for `cnt` iterations, then times an equivalent loop calling `sqlite3_snprintf()`, cycling through `aVal` by modulo. It prints both timings and a winner ratio.

## State and Persistence Behavior
There is no database state. State consists of the static value table, a local output buffer, and timing variables. Results are not persisted.

## Dependencies and Integration Points
It depends on public `sqlite3.h`, SQLite's printf implementation, standard `sprintf`, platform time APIs, and linking against SQLite plus math/thread/dl libraries as needed by the amalgamation.

## Risks and Edge Cases
The benchmark does not validate formatted output, only speed. Wall-clock timing is susceptible to CPU frequency changes, scheduler noise, libc implementation, compiler optimization, and `COUNT` size. `sprintf()` is intentionally used with a large buffer, so this is not a safety test.

## Test Signals
Output gives timing metrics for each formatter and a relative speed statement. It is a performance signal, not a correctness pass/fail except for argument validation.
