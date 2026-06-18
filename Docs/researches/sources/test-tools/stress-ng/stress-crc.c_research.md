# sources/test-tools/stress-ng/stress-crc.c

## Purpose
This stressor exercises CRC calculations across 8-, 16-, 32-, and 64-bit widths, multiple data element widths, and normal versus reverse bit ordering. It also validates compiler CRC builtins against software fallback implementations by comparing fixed input data to endian-specific expected results.

## Important APIs, Types, And Functions
`stress_crc_func_t` is the common CRC callback signature, and `stress_crc_method_t` records function, print width, expected result, and method name. Implementations include `stress_crc_crc8_data8()`, `stress_crc_crc16_data8()`, `stress_crc_crc16_data16()`, CRC32 variants, optional CRC64 variants, and reverse CRC counterparts. Each function uses a compiler builtin when available or a bitwise polynomial fallback otherwise. `stress_crc()` drives execution, validation, per-method metrics, and total Mbit/s reporting.

## Control Flow
Static aligned test data is interpreted as bytes, 16-bit words, 32-bit words, or 64-bit words depending on method. `stress_crc()` zeroes a metrics array, waits for synchronization, then repeatedly runs every method for `CRC_LOOPS` iterations while the stressor should continue. A mismatch logs the method name, actual value, and expected value, marks failure, and stops the run. On completion it emits per-method operations-per-second metrics and aggregate CRC throughput.

## State And Persistence
State is limited to fixed input data, the compile-time method table, and per-run metrics. There is no external persistence. Expected values are selected separately for little-endian and non-little-endian builds, and 64-bit methods are compiled only when `ULONG_MAX` indicates a 64-bit platform.

## Dependencies And Integration Points
The file depends on compiler-provided CRC builtins when present, stress-ng bit-reversal helpers for reverse CRC fallbacks, timing/metrics APIs, and architecture endian macros. It registers as CPU/compute work with `VERIFY_ALWAYS` and advertises enough metric slots for every method plus aggregate throughput.

## Risks
Expected results are sensitive to byte order, data packing, and builtin semantics. If a compiler builtin implements a different reflected/non-reflected convention than assumed, this stressor will surface it as a failure. Fallback loops step by element width and assume the fixed data length is compatible with every grouping. Per-method metrics are meaningful only when methods have nonzero duration.

## Test Signals
Signals include exact expected CRC values on little- and big-endian targets, correct inclusion/exclusion of 64-bit methods, matching behavior between builtins and fallbacks, and nonzero per-method and aggregate metrics. Build-matrix testing with and without each `HAVE_BUILTIN_*` macro is especially valuable.
