# sources/test-tools/ltp/testcases/kernel/syscalls/sigsuspend/sigsuspend02.c

## Purpose
Verify that sigsuspend(2) fails with - EFAULT mask points to memory which is not a valid part of the
process address space.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigsuspend`; types `struct tst_test`; harness
APIs `tst_test`, `tst_get_bad_addr`, `TST_EXP_FAIL`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`. Local functions include `setup`, `verify_sigsuspend`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
expected errno/status values `EFAULT`.
