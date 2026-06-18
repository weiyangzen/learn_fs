<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testrun.c -->
# sources/sync-backup/rsync/testrun.c

Purpose: small C wrapper that runs a testsuite shell script with a timeout and returns the child script's exit status.

Important APIs/types/functions: `main()`, constants `DEFAULT_TIMEOUT_SECS` and `TESTRUN_TIMEOUT`.

Control flow: parse timeout from the environment or default to 5 minutes, fork, in the child replace `argv[0]` with `sh` and `execvp()` the provided script/options, and in the parent poll `waitpid(..., WNOHANG)` once per second. If elapsed sleeps exceed the timeout, send SIGTERM and exit 1. If the child exits normally, return its status; if it dies by signal, return 255.

State and persistence behavior: creates a child process and may terminate it. No files are directly mutated.

Dependencies and integration points: depends on POSIX fork/exec/wait/kill and rsync portability headers. It is part of the rsync test harness, guarding shell tests from hanging indefinitely.

Risks: timeout check uses `slept++ > timeout_secs`, so actual timeout is roughly one second beyond the configured value. It sends only SIGTERM, not SIGKILL, so stubborn descendants may survive. It only reports the direct child's normal exit status.

Test signals: run with a fast successful script, a failing script, a script that exits by signal, and a sleep longer than `TESTRUN_TIMEOUT` to confirm exit mapping and timeout diagnostics.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testrun.c -->
