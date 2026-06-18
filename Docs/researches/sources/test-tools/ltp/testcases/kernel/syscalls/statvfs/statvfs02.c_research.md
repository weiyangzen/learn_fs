# sources/test-tools/ltp/testcases/kernel/syscalls/statvfs/statvfs02.c

## Purpose
Verify that statvfs() fails with: - EFAULT when path points to an invalid address. - ELOOP when too
many symbolic links were encountered in translating path. - ENAMETOOLONG when path is too long. -
ENOENT when the file referred to by path does not exist. - ENOTDIR a component of the path prefix of
path is not a directory.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statvfs`; types `struct statvfs`, `struct
tcase`, `struct tst_test`; safe wrappers `SAFE_SYMLINK`, `SAFE_TOUCH`; harness APIs `tst_test`,
`tst_get_bad_addr`, `TST_EXP_FAIL`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_tmpdir`. Local functions include `setup`, `run`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
expected errno/status values `EFAULT`, `ELOOP`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.
