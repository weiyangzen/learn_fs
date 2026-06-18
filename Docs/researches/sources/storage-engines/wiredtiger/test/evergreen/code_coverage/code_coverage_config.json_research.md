<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_config.json -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_config.json

Purpose: drives broad code coverage execution. It defines setup actions to configure a coverage build and a long ordered `test_tasks` list spanning csuite binaries, cppsuite workloads, Python suite tests, examples, `wt` utility commands, ctest filters, and disaggregated hook tests.

Data contract: top-level keys are `_comments`, `setup_actions`, and `test_tasks`. The setup uses `cmake --preset linux-gcc` with coverage and inline-function flags, `ninja -j 16`, creates `WT_HOME_COVERAGE`, runs `ex_hello`, and loads `test_table.json`. `parallel_code_coverage.py` and `per_test_code_coverage.py` expect exactly these keys and command strings.

State and persistence: setup creates build directories and test data used by later commands. The task list is ordered by expected duration so the parallel queue finishes efficiently; `parallel_code_coverage.py --optimize_test_order` can rewrite this file.

Dependencies and integration: referenced by `coverage-report-per-test.sh` and likely Evergreen coverage tasks. Commands assume execution from a copied coverage build directory where `../test/...`, `test/csuite/...`, and `./wt` paths resolve.

Risks and test signals: JSON comments are embedded as strings because JSON has no comments. Duplicate tasks exist intentionally or accidentally and may skew coverage/runtime. Any command containing shell syntax is later split on whitespace, so complex quoting is fragile.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_config.json -->
