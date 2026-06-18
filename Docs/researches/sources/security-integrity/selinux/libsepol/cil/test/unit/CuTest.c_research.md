# sources/security-integrity/selinux/libsepol/cil/test/unit/CuTest.c

## Purpose
`CuTest.c` implements the lightweight CuTest 1.5 unit test framework vendored for the CIL tests. It supplies dynamic strings, test case execution, assertion failure reporting, and suite aggregation.

## Important APIs, Types, And Functions
String helpers include `CuStrAlloc()`, `CuStrCopy()`, `CuStringInit()`, `CuStringNew()`, `CuStringDelete()`, `CuStringResize()`, `CuStringAppend()`, `CuStringAppendChar()`, `CuStringAppendFormat()`, and `CuStringInsert()`.

Test-case helpers include `CuTestInit()`, `CuTestNew()`, `CuTestDelete()`, `CuTestRun()`, `CuFailInternal()`, `CuFail_Line()`, and assertion implementations for boolean, string, int, double, and pointer comparisons. Suite helpers include `CuSuiteInit()`, `CuSuiteNew()`, `CuSuiteDelete()`, `CuSuiteAdd()`, `CuSuiteAddSuite()`, `CuSuiteRun()`, `CuSuiteSummary()`, and `CuSuiteDetails()`.

## Control Flow
`CuTestRun()` installs a `jmp_buf`, marks a test as run, and invokes the test function. Assertion failures call `CuFailInternal()`, which prefixes file/line information, stores the message, marks the test failed, and uses `longjmp()` to stop the test. `CuSuiteRun()` iterates suite entries and increments `failCount` for failed tests. Summary output emits one `.` or `F` per test; details output either reports `OK` or lists numbered failures with messages and run/pass/fail totals.

## State And Persistence
All state is in allocated `CuString`, `CuTest`, and `CuSuite` structures. Failure messages point into allocated `CuString` buffers that are intentionally retained for reporting. No persistent files are written.

## Dependencies And Integration Points
The implementation uses `assert`, `setjmp`, `stdlib`, `stdio`, `string`, and `math`, and exposes its API through `CuTest.h`. It is used by `AllTests.c`, `CilTest.c`, and individual CIL test files.

## Risks
`CuStringAppendFormat()` uses `vsprintf()` into a fixed `HUGE_STRING_LEN` buffer, which is a classic overflow risk if a very long formatted message is produced. `CuSuiteAdd()` enforces `MAX_TEST_CASES` with `assert()`, so release builds with `NDEBUG` could write past the fixed suite array. `CuSuiteAddSuite()` transfers test pointers without freeing the container suite, so ownership is simple but can leak containers in short-lived binaries. Failure control flow relies on `setjmp`/`longjmp`, so test code with cleanup requirements can leak unless structured carefully.

## Test Signals
The framework reports visible stdout summaries and failure details. It has no self-tests in this subset; confidence comes from its small stable implementation and use by the broader CIL test harness.
