# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice05.c

## Purpose
Functional test for splice(2): pipe <-> socket This test case tests splice(2) from a pipe to a
socket and vice versa.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_test`, `struct
tst_option`; constants/macros `AF_UNIX`; safe wrappers `SAFE_MALLOC`, `SAFE_PIPE`,
`SAFE_SOCKETPAIR`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `SAFE_READ`, `SAFE_CLOSE`; harness APIs
`tst_test`, `tst_parse_int`, `tst_brk`, `tst_res`, `tst_option`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `setup`, `cleanup`, `pipe_socket`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TINFO`, `TERRNO`; expected errno/status
values `EINVAL`.
