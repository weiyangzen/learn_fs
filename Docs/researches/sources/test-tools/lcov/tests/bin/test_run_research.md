# sources/test-tools/lcov/tests/bin/test_run

Purpose: legacy Bash helper that runs one test script, records command output, timing, memory, result status, and failure excerpts in the shared test log.

Important APIs: usage `test_run <testname> <cmdline> [--script-args args] [--coverage db]`. It sources `bin/common` for logging functions and uses environment variables such as `TOPDIR`, `LOGFILE`, `COUNTFILE`, and `TIMEFILE`.

Control flow and persistence: parses options, configures Perl Devel::Cover wrapping for `.pl` scripts when coverage is requested, probes GNU `time -v`, announces the test, appends command/output headers to `LOGFILE`, runs the script through `bash -c`, captures pipeline status, parses timing output, scans for unexpected `uninitialized`, records result and metrics to `COUNTFILE`, prints skip reasons or failure excerpts, and exits with the test status.

Dependencies and integration: used by shell-based tests and compatible with `testsuite_init/exit`. Depends on Bash, `time`, `stat`, `tail`, `grep`, and helper functions from `bin/common`.

Risks and test signals: command construction via `bash -c "$INVOKE_COVER $SCRIPT $OPTS"` is quoting-sensitive. Pipeline status handling assumes Bash. The helper itself is validated indirectly by every shell test that uses it.
