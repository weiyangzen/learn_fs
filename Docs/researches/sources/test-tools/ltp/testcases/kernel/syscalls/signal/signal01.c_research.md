# sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal01.c

## Purpose
Test SIGKILL for these items: 1. SIGKILL can not be set to be ignored, errno:EINVAL (POSIX). 2.
SIGKILL can not be reset to default, errno:EINVAL (POSIX). 3. SIGKILL can not be set to be caught,
errno:EINVAL (POSIX). 4. SIGKILL can not be ignored. 5. SIGKILL is reset to default failed but
processed by default. 6. SIGKILL can not be caught.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `signal`; types `struct tcase`, `struct
tst_test`; constants/macros `SIGKILL`, `SIG_IGN`, `SIG_DFL`; safe wrappers `SAFE_FORK`,
`SAFE_WAITPID`, `SAFE_KILL`; harness APIs `tst_test`, `TST_EXP_FAIL2`, `TST_EXP_EQ_SSZ`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`,
`.forks_child`. Local functions include `catchsig`, `do_test`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; changes per-process signal
dispositions, masks, pending queues, or alternate signal stack state. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TFAIL`; expected errno/status values `EINVAL`.
