# sources/test-tools/fio/mock-tests/Makefile

Purpose: build and run isolated fio mock tests, currently focused on latency precision.

Important targets/variables: `CC`, `CFLAGS`, `TEST_DIR`, `LIB_DIR`, `BUILD_DIR`, `TESTS`, `all`, `test`, `test-tap`, `test-%`, `clean`, and `help`.

Control flow: `all` creates `build` and compiles each test from `tests/*.c` with the TAP header dependency. `test` runs built binaries directly and counts failures. `test-tap` uses `prove -v` when available, otherwise falls back to direct execution.

State/persistence: creates and removes `mock-tests/build`; test output is printed to stdout/stderr. No integration with the top-level fio test runner is shown in this file.

Dependencies/integration: requires a C compiler, math library flag in `CFLAGS`, TAP-compatible test programs, and optionally Perl `prove`.

Risks/test signals: `-lm` appears in `CFLAGS` before the source/output in the compile rule, which can matter for linkers that require libraries after objects. Tests should run `make test` on target toolchains and verify `test-%` target names match declared test names.
