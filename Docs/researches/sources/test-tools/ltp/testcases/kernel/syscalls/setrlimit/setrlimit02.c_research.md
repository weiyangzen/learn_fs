# sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit02.c

## Purpose
Testcase to test the different errnos set by :manpage:`setrlimit(2)` system call.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setrlimit`; types `struct rlimit`, `struct
tcase`, `struct passwd`, `struct tst_test`; constants/macros `RLIMIT_NOFILE`; safe wrappers
`SAFE_GETPWNAM`, `SAFE_SETUID`, `SAFE_GETRLIMIT`; harness APIs `tst_test`, `TEST`, `tst_res`,
`tst_strerrno`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_root`. Local functions include `verify_setrlimit`, `setup`.

## State and persistence behavior
The test changes process credentials for the running process or child; changes resource limits in
the current process or child process. State is scoped to the LTP process tree unless a privileged
syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values `EINVAL`,
`EPERM`.
