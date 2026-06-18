<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/attach-f-p.c -->
## sources/test-tools/strace/tests/attach-f-p.c

Purpose: Multithreaded tracee for testing `strace -f -p` attach behavior across threads.

Important APIs/types/functions: Uses pthreads, `pipe`, `read`, `write`, `pthread_create`, `pthread_join`, `syscall(__NR_gettid)`, `fstat`, `sleep`, `chdir`, and fixed pid-prefixed printf formatting.

Control flow: Creates three worker threads blocked on per-thread pipes, writes a newline to signal readiness, waits until the peer has written enough output to stdout, releases each thread one at a time, joins it and prints expected failed `chdir` output with that thread tid, then prints parent `chdir` failure and exit.

State and persistence: Maintains in-process pipes and threads only; no files except stdout coordination.

Dependencies and integration: Linked with pthread by `Makefile.am`; paired with `attach-f-p-cmd.c` and attach test scripts to validate following threads while attached.

Risks: Timing-sensitive coordination uses stdout file size and sleeps to let tracer catch up. Environments where stdout is not seekable/regular can affect `fstat` assumptions.

Test signals: Output should include child thread tids, parent pid, failed `chdir` lines with `ENOENT`, and clean exits in expected order.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/attach-f-p.c -->
