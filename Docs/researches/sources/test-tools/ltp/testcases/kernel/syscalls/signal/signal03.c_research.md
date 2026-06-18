# sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal03.c

## Purpose
This LTP test source exercises `signal` syscall behavior in `signal03.c`.

## Important APIs, types, and functions
Important interfaces include types `struct tst_test`; constants/macros `SIGHUP`, `SIGINT`,
`SIGQUIT`, `SIGILL`, `SIGTRAP`, `SIGABRT`, `SIGIOT`, `SIGBUS`, `SIGFPE`, `SIGUSR1`, `SIGSEGV`,
`SIGUSR2`, `SIGPIPE`, `SIGALRM`, `SIGTERM`, `SIGSTKFLT`, `SIGCHLD`, `SIGCONT`; safe wrappers
`SAFE_SIGNAL`, `SAFE_KILL`; harness APIs `tst_test`, `TST_EXP_EQ_SSZ`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `sighandler`, `do_test`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.
