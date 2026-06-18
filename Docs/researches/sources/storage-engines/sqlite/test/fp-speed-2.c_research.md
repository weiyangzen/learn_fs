# sources/storage-engines/sqlite/test/fp-speed-2.c

## Purpose
`fp-speed-2.c` benchmarks decimal-to-binary floating-point conversion by comparing C library `atof()` with SQLite's internal `sqlite3AtoF()` exposed through `SQLITE_TESTCTRL_ATOF`.

## Important APIs, Types, and Functions
- Test data: `aVal[]` holds decimal mantissa strings.
- `fpLiteral()` synthesizes literals by taking prefixes of mantissas and appending exponents from -200 to +200.
- `timeOfDay()` is the same platform-aware microsecond timer pattern used by `fp-speed-1.c`.
- `main()` measures loop overhead, `atof()`, and `sqlite3_test_control(SQLITE_TESTCTRL_ATOF, ...)`.

## Control Flow
The program requires `COUNT >= 100`. It first measures test overhead by generating literals and adding a simple double value into checksum buckets. It subtracts that overhead from later `atof()` and `sqlite3AtoF()` timings. Checksums are accumulated into `arSum[401]` buckets keyed by exponent index to inhibit dead-code elimination and provide a coarse comparability signal.

## State and Persistence Behavior
There is no database state. All generated literals and sums are stack/local state, and no files are read or written.

## Dependencies and Integration Points
It depends on SQLite test-control support for `SQLITE_TESTCTRL_ATOF`, standard `atof`, `sqlite3.h`, and platform timing APIs. It is useful only in builds where the relevant test control is available.

## Risks and Edge Cases
The benchmark uses generated prefixes that are not necessarily identical to real SQL parser workloads. Timing subtracts a measured overhead loop, which can become noisy if `COUNT` is too small. The checksum is not a rigorous correctness oracle for conversion equivalence.

## Test Signals
Output reports overhead, net ns/test for `atof()` and `sqlite3AtoF()`, checksums, and relative speed. Argument validation is the only hard failure path.
