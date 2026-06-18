# sources/security-integrity/selinux/libsepol/tests/test-ebitmap.h

## Purpose
This header exposes the ebitmap CUnit suite hooks.

## Important APIs, Types, And Functions
It includes `<CUnit/Basic.h>` and declares `ebitmap_test_init()`, `ebitmap_test_cleanup()`, and `ebitmap_add_tests(CU_pSuite suite)`.

## Control Flow
The test runner initializes random/debug state, registers the bitmap test cases, and calls cleanup through these functions.

## State And Persistence Behavior
The header contains no state. The implementation allocates and destroys bitmap state per test.

## Dependencies And Integration Points
It integrates low-level ebitmap tests with the libsepol CUnit runner.

## Risks And Edge Cases
Only suite-level hooks are exposed; individual test functions are static in the implementation, which is good for encapsulation but limits selective external invocation.

## Test Signals
Compilation and successful registration of all ebitmap tests are the header-level signals.
