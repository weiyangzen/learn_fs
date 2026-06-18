# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_post.h

## Purpose
This header declares post-processing comparator tests for CuTest registration.

## Important APIs, Types, And Functions
It includes `CuTest.h` and declares tests for filecon, portcon, genfscon, netifcon, nodecon, and fsuse comparator order. Each declaration follows the pattern `void test_cil_post_<object>_compare_<case>(CuTest *tc)`.

## Control Flow
There is no executable control flow. `CilTest.c` includes this header and registers many of the declared comparator tests into the test suite.

## State And Persistence
The header stores no state and performs no persistence. It is a compile-time contract between the comparator test implementation and suite registrar.

## Dependencies And Integration Points
It integrates `test_cil_post.c` with CuTest and the CIL unit suite. The implementation depends on `cil_post.h` and CIL internal object initialization helpers.

## Risks
The header declares portcon tests, but the suite registration excerpt did not show portcon registrations alongside the other post tests. If they are not registered elsewhere, portcon implementation coverage may compile but not run. As with other headers in this directory, declaration drift can hide intended test coverage until link or registration changes expose it.

## Test Signals
The declaration list documents intended comparator coverage for ordering branches and equality cases in post-processing records.
