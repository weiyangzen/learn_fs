# sources/test-tools/ltp/testcases/kernel/syscalls/signal/signal02.c

## Purpose
This LTP test source exercises `signal` syscall behavior in `signal02.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `signal`; types `struct tst_test`;
constants/macros `SIGKILL`, `SIGSTOP`, `SIG_IGN`; harness APIs `tst_test`, `TST_EXP_FAIL2`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `do_test`.

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
expected errno/status values `EINVAL`.
