# sources/test-tools/kdevops/playbooks/python/workflows/fstests/gen_results_summary.py

Purpose: Library for scanning fstests xUnit results, printing human-readable summaries, and optionally merging xUnit test suites.

Key APIs and flow: `get_results()` finds result XML files; `parse_timestamp()` orders suites; property helpers read and remove JUnit properties; `print_summary()` writes per-suite counts and either verbose test rows or failed/error test lists. `gen_results_summary()` loads all reports, copies properties from the first report, optionally applies `ltm-run-stats`, prints header, sorted summaries, totals, trailer, and writes an atomic-ish merged XML via `.new`/`.bak`.

State, dependencies, integration: Depends on `junitparser`. Reads result XML and optional `ltm-run-stats`; may write text output and merged XML. Integrated by the wrapper script and fstests reporting workflows.

Risks and test signals: Assumes `reports[0].child(Properties)` exists; `failed_tests()` only handles direct `Failure` result shape and is unused; `sys.exc_clear()` is Python 2 legacy but guarded. Tests should cover timezone timestamps, LTM mode, missing properties, verbose small suites, merge backup behavior, skipped/errors/failures.
