# sources/test-tools/ltp/testcases/kernel/syscalls/sigrelse/sigrelse01.c

## Purpose
OS Test - Silicon Graphics, Inc. Eagan, Minnesota TEST IDENTIFIER : sigrelse01 Releasing held
signals. PARENT DOCUMENT : sgrtds01 sigrelse system call AUTHOR : Bob Clark : Rewrote 12/92 by
Richard Logan CO-PILOT : Dave Baumgartner DATE STARTED : 10/08/86 TEST ITEMS 1. sigrelse turns on
the receipt of signals held by sighold. SPECIAL PROCEDURAL REQUIRMENTS None DETAILED set up pipe for
parent/child communications fork off a child process parent(): set up for unexpected signals wait
for child to send ready message over pipe send all catchable signals to child process send alarm
signal to speed up timeout wait for child to terminate and check exit value if exit value is EXIT_OK
get message.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sighold`, `sigrelse`, `signal`, `pipe`, `fork`,
`kill`, `alarm`, `write`, `read`; constants/macros `SIG_CAUGHT`, `SIGCANCEL`, `SIGTIMER`, `SIGTERM`,
`SIG_ERR`, `SIGALRM`, `SIGKILL`, `SIGSTOP`, `SIGTSTP`, `SIGCONT`, `SIGNOBDM`, `SIGTTIN`, `SIGTTOU`,
`SIGPTINTR`, `SIGSWAP`, `SIGRTMIN`, `SIGRTMAX`; safe wrappers `SAFE_WAIT`, `SAFE_PIPE`; harness APIs
`TEST`, `tst_res`, `tst_parse_opts`, `tst_count`, `tst_fork`, `tst_brkm`, `tst_exit`, `tst_resm`,
`tst_sig`, `tst_tmpdir`, `tst_rmdir`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `setup`,
`cleanup`, `parent`, `child`, `timeout`, `setup_sigs`, `handler`, `wait_a_while`, `write_pipe`,
`set_timeout`, `clear_timeout`, `getout`, `choose_sig`, `sighold`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; changes per-process signal
dispositions, masks, pending queues, or alternate signal stack state. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness, legacy safe macro helpers, temporary directory
support. The file is built by the syscall directory Makefile and executed as part of the LTP kernel
syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TWARN`, `TERRNO`; expected errno/status values
`ESRCH`, `EOF`.
