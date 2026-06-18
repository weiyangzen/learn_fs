# sources/test-tools/ltp/testcases/kernel/syscalls/sigaction/sigaction01.c

## Purpose
Test some features of sigaction (see below for more details) ALGORITHM Use sigaction(2) to set a
signal handler for SIGUSR1 with a certain set of flags, set a global variable indicating the test
case, and finally send the signal to ourselves, causing the signal handler to run. The signal
handler then checks the signal handler to run. The signal handler then checks certain conditions
based on the test case number. There are 4 test cases: 1) Set SA_RESETHAND and SA_SIGINFO. When the
handler runs, SA_SIGINFO should be set. 2) Set SA_RESETHAND. When the handler runs, SIGUSR1 should
be masked (SA_RESETHAND makes sigaction behave as if SA_NODEFER was not set). 3) Same as case #2,
but when the.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigaction`, `sigemptyset`, `sigaddset`,
`sigprocmask`, `kill`; types `struct sigaction`; constants/macros `SIGUSR1`, `SIG_BLOCK`; harness
APIs `tst_resm`, `TEST`, `tst_parse_opts`, `tst_count`, `tst_brkm`, `tst_exit`.

## Control flow
The legacy LTP `main()` parses standard options, calls `setup()`, loops with `TEST_LOOPING()`, runs
the syscall scenario, then calls `cleanup()` and `tst_exit()`. Helper functions include `setup`,
`cleanup`, `handler`, `set_handler`.

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
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TWARN`.
