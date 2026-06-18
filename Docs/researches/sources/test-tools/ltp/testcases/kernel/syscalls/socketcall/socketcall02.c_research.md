# sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/socketcall02.c

## Purpose
Author: Sowmya Adiga <sowmya.adiga@wipro.com> This is a error test for the socketcall(2) system
call.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `socketcall`; types `struct test_case_t`, `struct
tst_test`; harness APIs `tst_test`, `tst_res`, `TEST`, `tst_syscall`, `tst_strerrno`,
`tst_get_bad_addr`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`.
Local functions include `verify_socketcall`, `setup`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/syscalls.h` compatibility wrappers, Linux
UAPI headers. The file is built by the syscall directory Makefile and executed as part of the LTP
kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery; obsolete or direct
syscall paths may be absent or emulated differently on newer architectures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TINFO`, `TTERRNO`, `TERRNO`; expected errno/status values
`EINVAL`, `EFAULT`.
