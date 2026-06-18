# sources/security-integrity/selinux/libsepol/tests/test-ebitmap.c

## Purpose
This CUnit suite tests libsepol extended bitmap behavior across initialization, comparison, set/get, ranges, boolean operations, complement operations, and randomized algebraic checks.

## Important APIs, Types, And Functions
Important functions are `ebitmap_init_random()`, `test_ebitmap_init_destroy()`, `test_ebitmap_cmp()`, `test_ebitmap_set_and_get()`, `test_ebitmap_init_range()`, `test_ebitmap_or()`, `test_ebitmap_and()`, `test_ebitmap_xor()`, `test_ebitmap_not()`, `test_ebitmap_andnot()`, `test_ebitmap__random_impl()`, `test_ebitmap__random()`, `ebitmap_test_init()`, and `ebitmap_add_tests()`.

## Control Flow
The suite creates small deterministic bitmaps around node boundaries such as 63/64, 191/192, 319/320, 1023/1024, and larger random bitmaps. Each operation writes a destination bitmap, compares against expected bitmaps, then destroys all temporary bitmaps.

## State And Persistence Behavior
There is no persistent external state. Runtime state is heap-backed `ebitmap_t` nodes. `ebitmap_test_init()` seeds `random()` with `time(NULL)` and disables sepol debug output.

## Dependencies And Integration Points
It depends on `<sepol/policydb/ebitmap.h>`, errno-style return codes, random number generation, and CUnit. These tests are direct low-level coverage for data structures used throughout policydb type sets.

## Risks And Edge Cases
Randomized tests are nondeterministic because the seed is current time, making rare failures harder to reproduce. The suite stresses boundary allocation but does not inject allocation failures.

## Test Signals
Signals include correct return codes (`-EINVAL`, `-EOVERFLOW`), correct cardinality/highest-bit values, exact operation results, and randomized per-bit equivalence for OR, AND, XOR, NOT, ANDNOT, and copy.
