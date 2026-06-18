# sources/security-integrity/selinux/libsepol/cil/test/unit/CuTest.h

## Purpose
`CuTest.h` is the public header for the vendored CuTest framework. It defines test, suite, and assertion APIs used by all CIL unit tests.

## Important APIs, Types, And Functions
The header defines `CUTEST_VERSION`, allocation/string constants, `CuString`, `CuTest`, `TestFunction`, and `CuSuite`. It declares string helpers, test lifecycle functions, assertion backends, and suite lifecycle/run/report functions. Public assertion macros wrap backend functions with `__FILE__` and `__LINE__`. `SUITE_ADD_TEST(SUITE, TEST)` creates a named test case from the function symbol and adds it to a suite.

## Control Flow
There is no executable flow in the header, but macros shape test execution. Assertion macros capture file/line at the call site. `SUITE_ADD_TEST` stringizes the test function name and passes the function pointer to `CuTestNew()`.

## State And Persistence
The declared structures hold in-memory string buffers, test function pointers, failure flags, failure messages, jump buffers, suite arrays, and failure counts. `MAX_TEST_CASES` fixes suite capacity at 1024 entries per suite.

## Dependencies And Integration Points
It includes `<setjmp.h>` and `<stdarg.h>`. It relies on consumers or `CuTest.c` including allocation declarations for `malloc` when using `CU_ALLOC`. CIL test files include this header directly to define tests and assertions.

## Risks
The fixed `MAX_TEST_CASES` limit can be exceeded by large suites, and the enforcement is in the C implementation assertion rather than in the macro. `CU_ALLOC` expands to `malloc` without including `<stdlib.h>` in the header. The header declares `CuStringRead()` but this subset's `CuTest.c` does not implement it, so using that declaration would create a link failure.

## Test Signals
Tests using this header produce CuTest-compatible assertion failures with file and line context. The broad use of `SUITE_ADD_TEST` in `CilTest.c` is the main integration signal.
