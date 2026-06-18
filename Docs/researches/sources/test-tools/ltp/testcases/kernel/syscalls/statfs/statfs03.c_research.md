# sources/test-tools/ltp/testcases/kernel/syscalls/statfs/statfs03.c

## Purpose
Verify that statfs(2) fails with errno EACCES when search permission is denied for a component of
the path prefix of path.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statfs`; types `struct passwd`, `struct statfs`,
`struct tst_test`; safe wrappers `SAFE_MKDIR`, `SAFE_GETPWNAM`, `SAFE_SETEUID`; harness APIs
`tst_test`, `TST_EXP_FAIL`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.needs_root`, `.needs_tmpdir`. Local functions include `setup`, `run`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount;
changes process credentials for the running process or child. State is scoped to the LTP process
tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support.
The file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
expected errno/status values `EACCES`.
