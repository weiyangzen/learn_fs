# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice02.c

## Purpose
Original reproducer for kernel fix bf40d3435caf NFS: add support for splice writes from v2.6.31-rc1.
http://lkml.org/lkml/2009/4/2/55 [ALGORITHM] - create pipe - fork(), child replace stdin with pipe -
parent write to pipe - child slice from pipe - check resulted file size and content. Referenced
kernel commit ids include `bf40d3435caf`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`, `stat`, `fork`; types `struct stat`,
`struct tst_test`, `struct tst_option`; safe wrappers `SAFE_CLOSE`, `SAFE_DUP2`, `SAFE_OPEN`,
`SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_PIPE`, `SAFE_FCNTL`, `SAFE_FORK`, `SAFE_WRITE`, `SAFE_WRITE_ALL`;
harness APIs `tst_test`, `tst_parse_int`, `tst_brk`, `TEST`, `tst_res`, `tst_reap_children`,
`tst_option`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.forks_child`, `.needs_tmpdir`. Local functions include `setup`, `do_child`, `run`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; maps or protects temporary
memory for buffers, alternate stacks, or coordination. State is scoped to the LTP process tree
unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TINFO`, `TTERRNO`, `TERRNO`.
