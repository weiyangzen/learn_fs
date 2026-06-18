# sources/test-tools/ltp/testcases/kernel/syscalls/statfs/statfs02.c

## Purpose
Tests for failures: - ENOTDIR A component of the pathname, which is not a directory. - ENOENT A
filename which doesn't exist. - ENAMETOOLONG A pathname which is longer than MAXNAMLEN. - EFAULT A
pathname pointer outside the address space of the process. - EFAULT A buf pointer outside the
address space of the process. - ELOOP A filename which has too many symbolic links.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statfs`, `close`; types `struct statfs`, `struct
test_case_t`, `struct tst_test`; constants/macros `SIGSEGV`; safe wrappers `SAFE_FORK`,
`SAFE_WAITPID`, `SAFE_CREAT`, `SAFE_SYMLINK`; harness APIs `tst_test`, `tst_safe_macros`,
`TST_EXP_FAIL`, `tst_res`, `tst_strstatus`, `tst_get_bad_addr`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.forks_child`, `.needs_tmpdir`. Local functions include `statfs_verify`, `setup`,
`cleanup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount; uses
child processes and wait/exit status as observable state. State is scoped to the LTP process tree
unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
LTP result macros `TPASS`, `TFAIL`; expected errno/status values `ENOTDIR`, `ENOENT`,
`ENAMETOOLONG`, `EFAULT`, `ELOOP`.
