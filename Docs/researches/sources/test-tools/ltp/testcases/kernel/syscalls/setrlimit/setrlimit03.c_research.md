# sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit03.c

## Purpose
Test :manpage:`setrlimit(2)` errnos: - EPERM when the super-user tries to increase RLIMIT_NOFILE
beyond the system limit. - EINVAL when rlim->rlim_cur is greater than rlim->rlim_max.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setrlimit`; types `struct rlimit`, `struct
tcase`, `struct tst_test`; constants/macros `RLIMIT_NOFILE`; safe wrappers `SAFE_FILE_SCANF`,
`SAFE_GETRLIMIT`; harness APIs `tst_test`, `TEST`, `tst_res`, `tst_strerrno`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_root`. Local functions include `verify_setrlimit`, `setup`.

## State and persistence behavior
The test changes resource limits in the current process or child process. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, Linux UAPI headers. The file is
built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values `EPERM`,
`EINVAL`.
