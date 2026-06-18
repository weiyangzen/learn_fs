<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/attach-f-p-cmd.c -->
## sources/test-tools/strace/tests/attach-f-p-cmd.c

Purpose: Companion command process for the `attach-f-p` test, producing predictable traced output with its pid.

Important APIs/types/functions: Uses `skip_if_unavailable("/proc/self/task/")`, `getpid`, `chdir`, and `sprintrc`.

Control flow: Skips if task information is unavailable, attempts to `chdir` into a known non-existent directory, prints the expected pid-prefixed syscall line and exit line.

State and persistence: No persistent state; only attempted cwd change.

Dependencies and integration: Coordinates with `attach-f-p.c` and the corresponding shell test to validate `strace -f -p` output ordering/format.

Risks: Output formatting uses fixed-width pid fields and must match tracer pid-prefix formatting.

Test signals: Expected two pid-prefixed lines for `chdir("attach-f-p.test cmd")` and clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/attach-f-p-cmd.c -->
