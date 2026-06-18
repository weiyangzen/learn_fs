# sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat03.c

## Purpose
check stat() with various error conditions that should produce EACCES, EFAULT, ENAMETOOLONG, ENOENT,
ENOTDIR, ELOOP.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `stat`; types `struct passwd`, `struct tcase`,
`struct stat`, `struct tst_test`; safe wrappers `SAFE_GETPWNAM`, `SAFE_SETUID`, `SAFE_MKDIR`,
`SAFE_TOUCH`, `SAFE_CHMOD`, `SAFE_SYMLINK`; harness APIs `tst_test`, `tst_eaccesdir`, `tst_enoent`,
`tst_enotdir`, `TST_EXP_FAIL`, `tst_get_bad_addr`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_root`, `.needs_tmpdir`. Local functions include `verify_stat`, `setup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount;
changes process credentials for the running process or child. State is scoped to the LTP process
tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support.
The file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
invalid-address tests can expose architecture-specific fault delivery.

## Test signals
expected errno/status values `EACCES`, `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `ELOOP`.
