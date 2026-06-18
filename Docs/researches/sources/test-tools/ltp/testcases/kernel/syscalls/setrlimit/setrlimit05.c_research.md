# sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit05.c

## Purpose
Test :manpage:`setrlimit(2)` for EFAULT when rlim points outside the accessible address space.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setrlimit`; types `struct rlimit`, `struct
tst_test`; constants/macros `RLIMIT_NOFILE`, `SIGSEGV`; safe wrappers `SAFE_FORK`, `SAFE_WAITPID`;
harness APIs `tst_test`, `TEST`, `tst_res`, `tst_strstatus`, `tst_get_bad_addr`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.forks_child`. Local functions include `verify_setrlimit`, `setup`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; changes resource limits in
the current process or child process. State is scoped to the LTP process tree unless a privileged
syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values `EFAULT`.
