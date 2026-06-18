# sources/test-tools/ltp/testcases/kernel/syscalls/setuid/setuid03.c

## Purpose
This test will switch to nobody user for correct error code collection. Verify setuid returns errno
EPERM when it switches to root_user.

## Important APIs, types, and functions
Important interfaces include types `struct passwd`, `struct tst_test`; safe wrappers
`SAFE_GETPWNAM`, `SAFE_SETUID`; harness APIs `tst_test`, `TST_EXP_FAIL`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.needs_root`. Local functions include `verify_setuid`, `setup`.

## State and persistence behavior
The test changes process credentials for the running process or child. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: compatibility-mode behavior depends on architecture, compiler flags, and kernel ABI
support; privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
expected errno/status values `EPERM`.
