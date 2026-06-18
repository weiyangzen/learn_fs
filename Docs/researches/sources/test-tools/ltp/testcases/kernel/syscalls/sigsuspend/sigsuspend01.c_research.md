# sources/test-tools/ltp/testcases/kernel/syscalls/sigsuspend/sigsuspend01.c

## Purpose
Verify the basic sigsuspend(2) syscall functionality: - sigsuspend(2) can replace process's current
signal mask by the specified signal mask and suspend the process execution until the delivery of a
signal. - sigsuspend(2) should return after the execution of signal handler and restore the previous
signal mask.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigsuspend`, `alarm`; types `struct sigaction`,
`struct tst_test`; constants/macros `SIGALRM`, `SIG_SETMASK`; safe wrappers `SAFE_SIGFILLSET`,
`SAFE_SIGPROCMASK`, `SAFE_SIGEMPTYSET`, `SAFE_SIGADDSET`, `SAFE_SIGACTION`; harness APIs `tst_test`,
`TEST`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`. Local functions include `sig_handler`, `verify_sigsuspend`, `setup`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values `EINTR`.
