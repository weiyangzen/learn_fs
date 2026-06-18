# sources/storage-engines/sqlite/tool/logest.c

## Purpose
`logest.c` is an interactive command-line calculator for SQLite's `LogEst` numeric representation, where values are approximately ten times base-2 logarithms. It converts between integers/floats and `LogEst`, performs multiply/add/reciprocal/log/NlogN operations on a small stack, and prints approximate numeric interpretations.

## Important APIs, Types, and Functions
- `typedef short int LogEst` defines the compact estimate type.
- `logEstMultiply(a,b)` adds two estimates, corresponding to multiplication in normal space.
- `logEstAdd(a,b)` approximates `log2(2^(a/10)+2^(b/10))*10` using a lookup table for deltas.
- `logEstFromInteger(sqlite3_uint64)` converts integer magnitudes to `LogEst`.
- `logEstToInt(LogEst)` converts estimates back to approximate unsigned integers, saturating at 64-bit max for very large estimates.
- `logEstFromDouble(double)` handles positive floating-point input, including subunit values and large values by inspecting IEEE-754 exponent bits.
- `isInteger()`, `isFloat()`, `showHelp()`, and `main()` implement stack-language parsing and output formatting.

## Control Flow
1. `main()` iterates over arguments and maintains a fixed stack `LogEst a[100]` with count `n`.
2. Numeric integer arguments are converted with `logEstFromInteger()`. Nonnegative floating arguments are converted with `logEstFromDouble()`. Arguments prefixed with `^` are interpreted directly as raw `LogEst`.
3. Operators mutate the stack: `+` combines top two with `logEstAdd`, `x` combines top two with `logEstMultiply`, `dup` duplicates, `inv` negates, `log` maps `N` to `log(N)`, and `nlogn` maps `N` to `N*log(N)`.
4. Unknown arguments call `showHelp()`. At the end, the stack is printed from top to bottom with raw estimate and approximate decimal/integer value.

## State and Persistence Behavior
All state is process-local stack memory. The program does not open databases or persist output; it only uses SQLite integer typedefs from `sqlite3.h`.

## Dependencies and Integration Points
- Depends on `sqlite3.h` for `sqlite3_uint64`.
- Mirrors SQLite planner estimation math used internally, making it useful for validating constants, estimates, and planner-cost intuition outside the main engine.
- Depends on standard C libraries for parsing and formatting.

## Risks and Edge Cases
- The stack has fixed size 100 and `dup`/push paths do not check overflow, so long argument lists can write past the array.
- `isFloat()` accepts broad character combinations and leaves final validation to `atof()` behavior; strings like repeated signs may pass syntactic screening.
- Negative floating-point arguments are rejected by the `z[0] != '-'` condition, while reciprocal values are represented through `inv`.
- `logEstFromDouble()` assumes 8-byte IEEE-754 `double` and 8-byte unsigned integer, enforced only by `assert()`.
- Output format uses `%lld` with `sqlite3_uint64` expressions; platform format mismatches are possible if typedefs differ.

## Test Signals
- Compare conversions for known inputs such as `1`, `2`, `10`, `100`, `123456`, `^123`, and fractional floats.
- Exercise stack operations: `2 3 x`, `100 200 +`, `10 dup x`, `100 log`, `100 nlogn`, and `10 inv`.
- Run with assertions enabled for floating conversions.
- Add overflow tests for more than 100 push operations if hardening this tool.
