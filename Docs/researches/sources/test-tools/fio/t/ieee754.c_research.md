# sources/test-tools/fio/t/ieee754.c

## Purpose
Round-trip test for fio's IEEE-754 double serialization helpers.

## Important APIs, Types, and Functions
Uses `fio_double_to_uint64()` and `fio_uint64_to_double()` from `lib/ieee754.h`. `main()` iterates a static set of representative doubles and returns the number of mismatches.

## Control Flow
Each value is converted to a `uint64_t`, converted back to `double`, printed with delta, and compared for exact equality. The sentinel `0.0` terminates the loop and is not tested.

## State and Persistence Behavior
No persistent state. Output is diagnostic stdout and the process exit code carries mismatch count.

## Dependencies and Integration Points
Validates conversion routines used anywhere fio needs stable binary or integer representation of floating-point values.

## Risks
The sentinel means zero itself is not tested despite appearing in the values array. Exact equality is appropriate for bit-preserving conversions but would fail if helpers intentionally normalized NaNs or other special values; those special values are not covered.

## Test Signals
Exit code zero indicates all listed values round-trip exactly. Additional useful signals would include zero, infinities, NaNs, subnormals, and negative zero.
