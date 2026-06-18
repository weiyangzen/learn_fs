# sources/security-integrity/selinux/libsepol/cil/test/unit/AllTests.c

## Purpose
`AllTests.c` is the executable entry point for the CIL unit and integration test binary. It creates CuTest suites, imports suite factories from `CilTest.c`, runs them, and prints combined details and summaries.

## Important APIs, Types, And Functions
The file declares suite factories `CilTreeGetSuite()`, `CilTreeGetResolveSuite()`, `CilTreeGetBuildSuite()`, and `CilTestFullCil()`. `RunAllTests()` disables CIL log output with `cil_set_log_level(0)`, creates a shared `CuString` output buffer, creates four `CuSuite` objects, adds generated suites into those objects with `CuSuiteAddSuite()`, runs each suite, appends details and summary, and prints the result. `main()` simply calls `RunAllTests()` and exits with `0`.

## Control Flow
The test binary always runs the base suite, resolve suite, build suite, and integration suite in sequence. For each suite it calls `CuSuiteRun()`, `CuSuiteDetails()`, and `CuSuiteSummary()`, appending into one output string. The process return code does not reflect failures because `main()` always returns `0`.

## State And Persistence
Runtime state is limited to in-memory CuTest suites and one `CuString` buffer. The file suppresses CIL logging globally for the process. It does not persist test results except to stdout.

## Dependencies And Integration Points
It depends on `CuTest.h` for the test framework and `../../src/cil_log.h` for log-level control. It integrates all suite registration functions from `CilTest.c` into one binary.

## Risks
Always returning `0` can hide failures from build systems that rely only on process status rather than parsing stdout. The suites allocated by `CuSuiteNew()` and `CuStringNew()` are not deleted before process exit, which is acceptable for a short-lived test binary but noisy under leak checkers. Log suppression may hide useful diagnostics when investigating failing tests.

## Test Signals
The output contains CuTest details and dot/F summaries for base, resolve, build, and integration suites. Any failure is visible in stdout details, not in the exit status.
