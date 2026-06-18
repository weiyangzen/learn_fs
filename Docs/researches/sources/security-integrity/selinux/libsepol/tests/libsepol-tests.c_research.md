# sources/security-integrity/selinux/libsepol/tests/libsepol-tests.c

## Purpose
`libsepol-tests.c` is the CUnit test runner for libsepol. It registers all local suites and runs them twice: once without MLS and once with MLS.

## Important APIs and Control Flow
`DECLARE_SUITE(name)` registers a suite from its init, cleanup, and add-tests functions. `do_tests()` initializes CUnit, registers `ebitmap`, `cond`, `linker`, `expander`, `deps`, `downgrade`, and `neverallow`, sets output mode, runs console or basic tests, collects failures, and cleans up. `main()` parses `--verbose` and `--interactive`, toggles global `mls` for two passes, and fails if either pass fails.

## State, Risks, and Test Signals
Global `int mls` is shared with suites to choose fixture variants. Verbose mode defaults on. Usage does not list `-h` even though the switch handles it via the default path. Passing execution is the aggregate signal that all registered suites pass in both MLS modes.
