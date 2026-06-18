# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice07.c

## Purpose
Iterate over all kinds of file descriptors and feed splice() with all possible combinations where at
least one file descriptor is invalid. We do expect the syscall to fail either with EINVAL or EBADF.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_fd`, `struct
tst_test`; harness APIs `tst_test`, `tst_fd`, `TST_EXP_FAIL2_ARR`, `tst_fd_desc`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test_all`, `.test`. Local
functions include `check_splice`, `verify_splice`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TINFO`; expected errno/status values `EINVAL`, `EBADF`.
