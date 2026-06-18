# sources/storage-engines/sqlite/tool/mkfptab.c

## Purpose
`mkfptab.c` generates C table initializers used by SQLite's floating-point power-of-ten conversion code. It constructs high-precision 256-bit approximations for powers of 10 from `1.0e-351` through `1.0e+347`, then emits compact `aBase[]`, `aScale[]`, and `aScaleLo[]` tables that let runtime code reconstruct the significant high bits of decimal powers using smaller lookup tables. With `--truth`, it also emits a full 128-bit reference table.

## Important APIs, Types, and Functions
- `typedef unsigned __int128 u128` and `typedef unsigned long long int u64` provide arithmetic building blocks.
- `struct u256 { u64 a[4]; }` represents a synthesized big-endian 256-bit unsigned integer.
- `u256_times_10`, `u256_times_2`, `u256_div_10`, and `u256_div_2` implement in-place scaled arithmetic with carries/remainders.
- Constants `SCALE_FIRST`, `SCALE_LAST`, `SCALE_COUNT`, and `SCALE_ZERO` define the exponent range and index of `1.0e+0`.
- `main()` parses `--round` and `--truth`, fills `aHi`, `aLo`, and `aE`, then prints C initializers.

## Control Flow
1. CLI parsing accepts `-round`/`--round` and `-truth`/`--truth`, otherwise exits with an unknown-option error.
2. For nonpositive decimal exponents, it initializes a normalized `u256` at the high bit, records high/low words and binary exponent, divides by 10, and renormalizes by multiplying by 2.
3. For positive decimal exponents, it initializes a shifted value, repeatedly multiplies by 10, renormalizes by dividing by 2 while carry appears in the top word, and records high/low words and exponent.
4. If `--truth` is set, it prints `aTruth[]` entries with 128 bits for every supported decimal power.
5. It prints `aBase[]` for powers 0 through 26.
6. It prints `aScale[]` and `aScaleLo[]` at 27-exponent intervals, with a special entry for exponent -1 replacing the zero slot. `--round` rounds `aScaleLo[]` high 32-bit values when bit 31 is set, except for the special case.

## State and Persistence Behavior
The program has no persistent state. It computes all arrays in stack-local `aHi`, `aLo`, and `aE` buffers and writes generated C text to standard output.

## Dependencies and Integration Points
- Requires compiler support for `__uint128_t`/`unsigned __int128`, available in GCC/Clang but not portable to all C compilers.
- Includes standard headers only.
- Its output is intended to be copied or generated into SQLite floating-point utility code, specifically the tables used by `powerOfTen()` in `util.c`.

## Risks and Edge Cases
- Portability is limited by `unsigned __int128`.
- The comments mention approximates accurate to "96 bytes" and "next 32 bites"; those are comment typos and should be interpreted as bits.
- Format strings use `%llx` and assume `u64` is compatible with `unsigned long long`.
- Arithmetic correctness depends on normalization loops preserving the intended significant bits across the full exponent range; changes need numerical validation, not just compile tests.
- The program writes code to stdout, so build scripts must redirect output deliberately.

## Test Signals
- Compile with GCC or Clang and run with no arguments, `--round`, `--truth`, and combined flags.
- Diff generated tables against checked-in SQLite table constants.
- Validate selected powers against high-precision decimal/binary calculations, especially boundaries `-351`, `-348`, `0`, `26`, `27`, and `+347`.
- Confirm unknown options exit nonzero with a diagnostic.
