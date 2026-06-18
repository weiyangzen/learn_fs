<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/PTRACE_SEIZE.sh -->
## sources/test-tools/strace/tests/PTRACE_SEIZE.sh

Purpose: Shell prerequisite helper that skips tests when the running kernel/tracer combination cannot use `PTRACE_SEIZE`.

Important APIs/types/functions: Uses `$STRACE -d -enone /`, redirects diagnostics to `$LOG`, searches with `grep -x`, and invokes the harness `skip_` function.

Control flow: Runs strace against `/` while ignoring command failure, then scans the debug log for the exact unsupported `PTRACE_SEIZE doesn't work` diagnostic. A match causes a skip; otherwise the caller continues.

State and persistence: Writes only the harness log file named by `$LOG`; no persistent state.

Dependencies and integration: Requires `init.sh`-style harness variables/functions and is listed as `check_SCRIPTS` in `Makefile.am`. It protects attach/ptrace-heavy tests from unsupported kernels.

Risks: The skip decision depends on a stable diagnostic string and debug output format. Localization or message changes would cause false negatives.

Test signals: Exercise on kernels with and without usable `PTRACE_SEIZE`, verifying that unsupported cases call `skip_` and supported cases leave the test active.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/PTRACE_SEIZE.sh -->
