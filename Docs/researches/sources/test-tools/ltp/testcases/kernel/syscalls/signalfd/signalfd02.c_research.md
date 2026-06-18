# sources/test-tools/ltp/testcases/kernel/syscalls/signalfd/signalfd02.c

## Purpose
Verify that signalfd(2) fails with: - EBADF when fd is invalid - EINVAL when fd is not a valid
signalfd file descriptor - EINVAL when flags are invalid.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `signalfd`; types `struct test_case_t`, `struct
tst_test`, `struct tst_buffers`; constants/macros `SIGNAL_FILE`, `SIGUSR1`, `SIG_BLOCK`; safe
wrappers `SAFE_SIGEMPTYSET`, `SAFE_SIGADDSET`, `SAFE_SIGPROCMASK`, `SAFE_OPEN`, `SAFE_CLOSE`;
harness APIs `tst_test`, `TST_EXP_FAIL2`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_tmpdir`. Local functions include `setup`, `cleanup`, `verify_signalfd`.

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
expected errno/status values `EBADF`, `EINVAL`.
