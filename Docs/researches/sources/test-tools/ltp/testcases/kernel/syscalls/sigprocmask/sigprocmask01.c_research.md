# sources/test-tools/ltp/testcases/kernel/syscalls/sigprocmask/sigprocmask01.c

## Purpose
Test Name: sigprocmask01 Verify that sigprocmask() succeeds to examine and change the calling
process's signal mask. Also, verify that sigpending() succeeds to store signal mask that are blocked
from delivery and pending for the calling process. Expected result: - sigprocmask() should return
value 0 on successs and succeed to change calling process's set of blocked/unblocked signals. -
sigpending() should succeed to store the signal mask of pending signal. Algorithm: Setup: Setup
signal handling. Create temporary directory. Pause for SIGUSR1 if option specified. Test: Loop if
the proper options are given. Execute system call Check return code, if system call failed
(return=-1) Log the errno.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigaction`, `sigemptyset`, `sigaddset`,
`signal`, `sigpending`, `sigprocmask`, `kill`; types `struct sigaction`, `struct to`;
constants/macros `SIGUSR1`, `SIGINT`, `SIG_BLOCK`, `SIG_UNBLOCK`; harness APIs `tst_parse_opts`,
`tst_count`, `TEST`, `tst_resm`, `tst_brkm`, `tst_exit`, `tst_sig`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `setup`,
`cleanup`, `sig_handler`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include legacy LTP `test.h` harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`.
