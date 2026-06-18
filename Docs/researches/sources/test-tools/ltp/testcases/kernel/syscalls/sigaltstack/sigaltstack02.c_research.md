# sources/test-tools/ltp/testcases/kernel/syscalls/sigaltstack/sigaltstack02.c

## Purpose
Verify that sigaltstack() fails with return value -1 and set expected errno: - EINVAL on invalid
value. - ENOMEM on stack is < MINSIGSTKSZ.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigaltstack`; types `struct test_case`, `struct
tst_test`; constants/macros `SIGSTKSZ`; safe wrappers `SAFE_MALLOC`; harness APIs `tst_test`,
`TST_EXP_FAIL`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_tmpdir`. Local functions include `check_sigaltstack`, `setup`, `cleanup`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
expected errno/status values `EINVAL`, `ENOMEM`.
