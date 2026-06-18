<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice04.c

Purpose: tests `vmsplice()` behavior on a full pipe: nonblocking mode must fail with `EAGAIN`, while blocking mode should sleep rather than write.

Important APIs/types/functions: `setup()` creates a pipe, obtains `F_GETPIPE_SZ`, allocates a buffer of that size, fills the pipe using `vmsplice()`, and stores the iovec. `vmsplice_test()` first calls with `SPLICE_F_NONBLOCK`, then forks a child that calls blocking `vmsplice()`. The parent uses `TST_PROCESS_STATE_WAIT(pid, 'S', 1000)` to confirm sleep and then kills the child.

Control flow/state: pipe fullness is established once in setup and consumed only by attempted writes. The child is expected to block until killed.

Dependencies/integration: requires Linux pipe-size fcntl, `SPLICE_F_NONBLOCK`, LTP process-state polling, and `.forks_child = 1`.

Risks/test signals: scheduler timing can affect the blocked-state check. Nonblocking success or wrong errno indicates pipe capacity/accounting regression; blocking child returning indicates incorrect full-pipe behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice04.c -->
