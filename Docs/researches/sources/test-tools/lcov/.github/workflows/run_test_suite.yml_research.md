# sources/test-tools/lcov/.github/workflows/run_test_suite.yml

Purpose: GitHub Actions workflow for lcov regression testing across selected GCC versions and Ubuntu runners, including install/uninstall verification and artifact capture.

Important APIs/types/functions: workflow triggers, read-only permissions, matrix strategy, `actions/checkout@v6`, apt package installation, CPAN install of `Memory::Process`, optional Ubuntu `resolute` repository for GCC 16, systemwide compiler symlink replacement, `make install`, `make uninstall`, `make check`, and `actions/upload-artifact@v7`.

Control flow: the matrix covers GCC 9, 10, 14, and 16 on Ubuntu 24.04, skipping 11-13 as equivalent coverage. Each job installs Perl, LLVM, Python, Sphinx, and GD dependencies; adds a future Ubuntu repo for GCC 16; rewires `/usr/bin` compiler and gcov command symlinks to the selected version; stages installation under `ROOT` with `PREFIX=/usr CFG_DIR=/etc`; uninstalls and diffs the staging root for leftovers; runs the test suite; then uploads `tests/test.log` and the whole `tests` directory.

State/persistence behavior: runner-local package installs and `/usr/bin` symlink changes are ephemeral. The staged install tree `ROOT` is created and expected to be empty after uninstall. Test logs and shrapnel are persisted as artifacts.

Dependencies/integration: exercises the project Makefile install/uninstall/check targets, docs build dependencies, gcov behavior across compiler versions, Perl modules documented in README, and tests under `tests`.

Risks/test signals: modifying system compiler symlinks is broad but isolated to the runner. GCC 16 depends on a future Ubuntu repository and may be fragile. The uninstall check is a strong signal for packaging hygiene; `make check` plus uploaded logs are the main behavioral test signals.
