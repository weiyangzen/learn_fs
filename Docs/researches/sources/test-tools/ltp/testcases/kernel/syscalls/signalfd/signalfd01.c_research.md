# sources/test-tools/ltp/testcases/kernel/syscalls/signalfd/signalfd01.c

## Purpose
Verify that signalfd() works as expected. - signalfd() can create fd, and fd can receive signal. -
signalfd() can reassign fd, and fd can receive signal.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `signalfd`; types `struct signalfd_siginfo`,
`struct tst_test`; constants/macros `SIGUSR1`, `SIG_BLOCK`, `SIGUSR2`; safe wrappers `SAFE_KILL`,
`SAFE_READ`, `SAFE_SIGEMPTYSET`, `SAFE_SIGADDSET`, `SAFE_SIGPROCMASK`, `SAFE_CLOSE`; harness APIs
`tst_test`, `TST_EXP_EQ_LI`, `TST_EXP_FD`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `check_signal`, `setup`, `cleanup`, `verify_signalfd`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.
