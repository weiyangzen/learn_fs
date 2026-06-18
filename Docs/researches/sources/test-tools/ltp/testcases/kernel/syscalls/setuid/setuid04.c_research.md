# sources/test-tools/ltp/testcases/kernel/syscalls/setuid/setuid04.c

## Purpose
Check if setuid behaves correctly with file permissions. The test creates a file as ROOT with
permissions 0644, does a setuid and then tries to open the file with RDWR permissions. The same test
is done in a fork to check if new UIDs are correctly passed to the son.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setuid`, `open`, `close`; types `struct passwd`,
`struct tst_test`; safe wrappers `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_TOUCH`; harness APIs
`tst_test`, `tst_fd`, `TEST`, `tst_res`, `tst_brk`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.forks_child`, `.needs_root`, `.needs_tmpdir`. Local functions include `dosetuid`,
`verify_setuid`, `setup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount;
changes process credentials for the running process or child; uses child processes and wait/exit
status as observable state. State is scoped to the LTP process tree unless a privileged syscall
changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support.
The file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: compatibility-mode behavior depends on architecture, compiler flags, and kernel ABI
support; privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TTERRNO`, `TERRNO`; expected errno/status values
`EACCES`.
