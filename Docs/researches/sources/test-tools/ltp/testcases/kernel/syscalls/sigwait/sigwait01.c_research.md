# sources/test-tools/ltp/testcases/kernel/syscalls/sigwait/sigwait01.c

## Purpose
This LTP test source exercises `sigwait` syscall behavior in `sigwait01.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigwait`; types `struct sigwait_test_desc`,
`struct tst_test`; constants/macros `SIGUSR1`; harness APIs `tst_test`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.forks_child`. Local functions include `my_sigwait`, `run`.

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
