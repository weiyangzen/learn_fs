<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/coverage-report-per-test.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/coverage-report-per-test.sh

Purpose: Evergreen wrapper for per-test coverage collection and changed-function reachability diagnostics.

Control flow: requires `is_patch` and `num_jobs`, runs `find_cmake.sh`, prints disk usage, creates `coverage_data` and `coverage_report`, creates a Python virtualenv, and installs gcovr/pygit2/requests dependencies. It downloads Metrix++, collects/export complexity data from `src`, then runs `code_coverage/per_test_code_coverage.py` with setup enabled, the main coverage config, absolute build dir base, job count, and absolute gcovr output dir. After tests it removes `build*copy*` directories, and for patch builds generates a filtered diff, HTML-friendly diff, logs it, and runs `per_test_code_coverage_report.py`. Finally it tars `coverage_data`.

State and persistence: writes virtualenv, coverage data/report directories, Metrix++ checkout/db, build dirs, diff files, and a tarball.

Dependencies and integration: called by Evergreen `coverage-report-per-test`. Depends on CMake, gcovr, Metrix++, coverage config JSON, git, and local report scripts.

Risks and test signals: very disk-heavy; cleanup occurs only after coverage tests. `rm -Rf build*copy*` prevents command-line length problems for later diff exclusion. Patch-only diagnostics write mostly to logs rather than structured output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/coverage-report-per-test.sh -->
