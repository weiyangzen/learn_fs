<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid07.c

Purpose: focused `waitid()` test that observes a `SIGSTOP`ped child with `WSTOPPED|WNOWAIT`, validates `CLD_STOPPED`, then continues the child.

Important APIs/types/functions: each test allocates `siginfo_t *infop` through LTP `.bufs` where needed and uses `SAFE_FORK()`, `waitid()`, `TST_EXP_PASS` or `TST_EXP_FAIL`, and `TST_EXP_EQ_LI` on `siginfo_t` fields. Tests involving stopped children use checkpoints and `SAFE_KILL()` to order signal delivery.

Control flow/state: process state is the core fixture: exited, running, stopped, continued, non-child, signal-killed, or core-dumping child depending on the file. Successful cases inspect `si_pid`, `si_status`, `si_signo`, and `si_code`; negative cases assert exact errno.

Dependencies/integration: integrates with LTP child reaping, checkpoint synchronization, temporary directory/core-limit setup for the SIGFPE case, and signal helpers. Files with `.forks_child` rely on the harness to clean remaining children.

Risks/test signals: timing-sensitive tests are those involving `SIGSTOP`/`SIGCONT` and `WNOHANG`; checkpoint barriers reduce races. Failures point to wait-class filtering, `siginfo_t` population, signal-state reporting, or errno regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitid/waitid07.c -->
