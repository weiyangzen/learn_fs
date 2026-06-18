<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/suite_subprocess.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/suite_subprocess.py

Purpose: Mixin for WiredTiger suite tests that need to run subprocesses, especially `run.py` test functions and the external `wt` utility, while preserving suite-style output checks and diagnostics.

Important APIs and types: `suite_subprocess` exposes file-output assertions (`has_error_in_file`, `check_no_error_in_file`, `check_file_content`, `check_file_contains`, `check_file_not_contains`, `check_empty_file`, `check_non_empty_file`), regex helper `convert_to_pattern`, diagnostic `show_outputs`, `run_subprocess_function`, and `runWt`.

Control flow: `run_subprocess_function` builds a `run.py -p --dir <directory> dotted.test.method` command, captures stdout/stderr in parent-directory files, optionally reports failures, and returns the exit status plus the generated WiredTiger home. `runWt` closes the live connection when requested, chooses `.libs/wt` when available, optionally wraps it in gdb/lldb, runs with input/output redirection, enforces expected success or failure, checks default output files are empty, and reopens the test connection/session.

State and persistence behavior: Subprocess calls create `subprocess.out`, `subprocess.err`, `wt.out`, `wt.err`, and test home directories. `runWt` forces flushability by closing the connection before external access and may rewrite verify URIs to `layered:` when the disagg hook is active.

Dependencies and integration points: Imports `wt_builddir` from `run.py`, `WiredTigerTestCase`, `wttest`, Python `subprocess`, and hook state such as `hook_names`. It is mixed into classes like backup tests and uses `close_conn`/`open_conn` supplied by `WiredTigerTestCase`.

Risks: File checks cap reads at 1 GiB but still can be expensive. Error detection is string based. `runWt` is skipped for tiered hooks because external utility invocation cannot reproduce injected tiered extension configuration. Debugger modes change normal capture behavior.

Test signals: Exit-code assertions, empty/non-empty output files, regex/content matches, and printed captured output on failure provide the primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/suite_subprocess.py -->
