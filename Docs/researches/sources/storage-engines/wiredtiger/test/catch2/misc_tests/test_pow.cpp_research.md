# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_pow.cpp

## Purpose
Tests small power-of-two utility functions used throughout WiredTiger.

## Important APIs, Types, And Functions
Calls `__wt_log2_int`, `__wt_ispo2`, and `__wt_rduppo2`.

## Control Flow
Separate test cases check log2 floor results, power-of-two predicates, and rounding up to a power-of-two multiple. Inputs include zero, small exact powers, non-powers, high 32-bit boundaries, and invalid non-power alignment values.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Depends on Catch2 and `wt_internal.h`. These utilities are general low-level helpers.

## Risks And Edge Cases
Documents intentional behavior that zero returns `0` for log2 and true for `ispo2`. `rduppo2` returns zero when the alignment argument is not a power of two.

## Test Signals
Exact integer return values are asserted for every input.
