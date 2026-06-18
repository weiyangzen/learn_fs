<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/acct.c -->
## sources/test-tools/strace/tests/acct.c

Purpose: Minimal decoder test for the `acct` syscall path argument.

Important APIs/types/functions: Calls `syscall(__NR_acct, sample)`, prints `sprintrc(rc)`.

Control flow: Uses a constant filename `acct_sample`, invokes `acct`, prints the decoded path and result, exits.

State and persistence: Does not create the accounting file; only passes a path string to the kernel.

Dependencies and integration: Depends on `tests.h`, `scno.h`, and generic syscall result formatting.

Risks: `acct` commonly requires privilege and may fail; the test treats failure as expected output, so the risk is syscall-number availability or unexpected errno formatting.

Test signals: Output line should be `acct("acct_sample") = ...` followed by clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/acct.c -->
