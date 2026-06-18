# sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/setxattr03.c

## Purpose
setxattr(2) to immutable and append-only files should get EPERM - Set attribute to a immutable file
- Set attribute to a append-only file.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `ioctl`, `setxattr`; types `struct test_case`,
`struct tst_test`; safe wrappers `SAFE_CREAT`, `SAFE_CLOSE`, `SAFE_UNLINK`; harness APIs `tst_test`,
`TEST`, `tst_res`, `tst_strerrno`, `tst_brk`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_root`, `.needs_tmpdir`. Local functions include `verify_setxattr`,
`fsetflag`, `setup`, `cleanup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support.
The file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TWARN`, `TTERRNO`, `TERRNO`; expected
errno/status values `EPERM`, `ENOTSUP`.
