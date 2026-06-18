# sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat04.c

## Purpose
This test checks that stat() executed on file provide the same information of symlink linking to it.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `stat`; types `struct stat`, `struct tst_test`,
`struct tst_buffers`; safe wrappers `SAFE_STAT`, `SAFE_MKFS`, `SAFE_MOUNT`, `SAFE_TOUCH`,
`SAFE_LINK`, `SAFE_CHOWN`, `SAFE_OPEN`, `SAFE_CLOSE`, `SAFE_SYMLINK`, `SAFE_UMOUNT`; harness APIs
`tst_test`, `tst_safe_stdio`, `TST_EXP_EQ_LI`, `tst_tmpdir_genpath`, `tst_device`, `tst_fill_fd`,
`tst_is_mounted`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`, `.needs_root`, `.needs_device`. Local functions include `run`, `setup`,
`cleanup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up; creates temporary
filesystem objects under the LTP temporary directory or test mount. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support,
scratch block device. The file is built by the syscall directory Makefile and executed as part of
the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
signal and timeout based assertions depend on scheduler timing; mount namespace, filesystem type,
and kernel version differences affect expected fields.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.
