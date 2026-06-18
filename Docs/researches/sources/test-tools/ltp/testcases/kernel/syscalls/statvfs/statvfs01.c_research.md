# sources/test-tools/ltp/testcases/kernel/syscalls/statvfs/statvfs01.c

## Purpose
Verify that statvfs() executes successfully for all available filesystems. Verify statvfs.f_namemax
field by trying to create files of valid and invalid length names.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statvfs`, `creat`; types `struct statvfs`,
`struct tst_test`; safe wrappers `SAFE_CLOSE`, `SAFE_TOUCH`; harness APIs `tst_test`, `tst_fs_type`,
`TST_EXP_PASS`, `TST_EXP_FD`, `TST_EXP_FAIL`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.needs_root`. Local functions include `run`, `setup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
expected errno/status values `ENAMETOOLONG`.
