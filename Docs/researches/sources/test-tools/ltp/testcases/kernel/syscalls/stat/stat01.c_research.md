# sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat01.c

## Purpose
Verify that, stat(2) succeeds to get the status of a file and fills the stat structure elements
regardless of whether process has or doesn't have read access to the file.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `stat`; types `struct passwd`, `struct tcase`,
`struct stat`, `struct tst_test`; safe wrappers `SAFE_GETPWNAM`, `SAFE_SETUID`, `SAFE_CHMOD`;
harness APIs `tst_test`, `TST_EXP_PASS`, `TST_EXP_EQ_LU`, `TST_EXP_EQ_LI`, `tst_fill_file`,
`tst_brk`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_root`, `.needs_tmpdir`. Local functions include `verify_stat`, `setup`.

## State and persistence behavior
The test changes process credentials for the running process or child. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support.
The file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TBROK`.
