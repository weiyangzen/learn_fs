# sources/test-tools/lcov/tests/bin/test_skip

Purpose: Bash helper to mark one test case as skipped and record a reason.

Important APIs: usage `test_skip <testname> <reason>`. It sources `bin/common`, sets `TESTNAME` and `REASON`, calls `t_announce` and `t_skip`, writes the reason to `LOGFILE`, and prints it indented to stdout.

Control flow and state: `TOPDIR` is discovered relative to the script. Empty reason text becomes `<no reason given>`. The script does not explicitly write to `COUNTFILE`; that behavior is likely encapsulated by `t_skip` from `bin/common`.

Dependencies and integration: used by tests that need to skip based on missing tools or unsupported environments. It relies on shell helper functions and shared log variables from `bin/common`.

Risks and test signals: reason text is unescaped shell text but only echoed/logged. If `bin/common` is missing or `TOPDIR` discovery fails, skip reporting fails. Test signal is suite summaries showing skipped counts and reasons.
