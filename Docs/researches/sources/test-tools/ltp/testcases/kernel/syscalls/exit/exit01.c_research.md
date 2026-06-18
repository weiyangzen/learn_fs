# sources/test-tools/ltp/testcases/kernel/syscalls/exit/exit01.c

Purpose: Legacy LTP test verifying that `exit()` status is reported correctly to a waiting parent.

Important APIs/types/functions: `test.h` harness globals `TCID`/`TST_TOTAL`, `tst_parse_opts`, `tst_fork`, `wait`, `tst_resm`, `TEST_LOOPING`, and `tst_exit`.

Control flow: Each loop forks one child that calls `exit(1)`. The parent waits, checks the returned pid, strips a core-dump bit from the low status byte, expects signal 0, and expects exit status 1.

State and persistence behavior: State is the child process exit status captured by `wait()`. No files or shared memory are used.

Dependencies and integration points: Uses old LTP signal/pause setup with `tst_sig(FORK, DEF_HANDLER, cleanup)`.

Risks and test signals: The test manually decodes wait status instead of `WIFEXITED`/`WEXITSTATUS`, so portability depends on historical status layout. Failures identify wrong pid, signal, or exit code.
