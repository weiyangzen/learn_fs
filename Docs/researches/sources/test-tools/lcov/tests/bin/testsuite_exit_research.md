# sources/test-tools/lcov/tests/bin/testsuite_exit

Purpose: legacy Bash suite finalizer that aggregates `test.counts`, appends final details to `test.log`, prints a colored summary, and sets the suite exit status.

Important APIs: no arguments. It sources `bin/common`, reads `COUNTFILE`, and uses `t_marker`, `t_detail`, and color variables.

Control flow and persistence: appends `end_time` to `COUNTFILE`, initializes success/failure/skipped/time/memory counters, parses count lines for `start_time`, `end_time`, `pass`, `fail`, `skip`, `elapsed`, and `resident`, redirects stdout/stderr to `LOGFILE` while preserving fd 3 for console summary, writes final log details, prints total/pass/fail/skip plus optional aggregate time/memory, and exits 1 if any failures occurred.

Dependencies and integration: called by shell test flows and by `runtests.py.cleanup()` for compatibility, although the Python runner also writes its own summary.

Risks and test signals: numeric aggregation uses Bash `let` and assumes well-formed count lines. It ignores killed/timeout statuses unless encoded as failures. Test signal is the final suite summary and nonzero exit on failure.
