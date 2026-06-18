# sources/test-tools/lcov/tests/genhtml/Makefile

Purpose: genhtml-specific test suite Makefile that includes common LCOV test infrastructure and enumerates genhtml test scripts.

Important variables/targets: includes `../common.mak`, sets `TESTS := full.sh zero.sh demangle.sh relative lambda exception simple filter function insensitive synthesize errs`, and records disabled legacy scripts in `DISABLED`. Overrides `clean` to remove genhtml local artifacts after common cleanup.

Control flow and persistence: when `make check` runs in this directory, `common.mak` dispatches the listed test scripts/directories through `runtests.py`. `clean` runs common `clean_echo` and `clean_subdirs`, then removes `*.log`, `out_*`, and `*.tmp`.

Dependencies and integration: relies entirely on common variables such as `GENHTML`, fixture info files, test helper binaries, and generated sources. The listed tests exercise genhtml rendering, demangling, relative paths, exception handling, filters, function views, case insensitivity, synthetic source, and error paths.

Risks and test signals: disabled tests are retained as documentation but not executed. The Makefile is intentionally small; failures usually indicate test script behavior or common infrastructure issues rather than this file. Signals are per-test results from the genhtml suite and cleanup artifact removal.
