# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount06.c

## Purpose
This test verifies that statmount() is correctly reading name of the filesystem type using
STATMOUNT_FS_TYPE. [Algorithm] - create a mount point - run statmount() on the mount point using
STATMOUNT_FS_TYPE - read results and check if contain the name of the filesystem.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`, `struct
ltp_statx`, `struct tst_test`, `struct tst_buffers`; constants/macros `STATMOUNT_FS_TYPE`,
`AT_FDCWD`, `STATX_MNT_ID_UNIQUE`; safe wrappers `SAFE_STATX`; harness APIs `TST_EXP_PASS`,
`tst_device`, `TST_EXP_EQ_LI`, `TST_EXP_EQ_STR`, `tst_test`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`. Local functions include `run`, `setup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up. State is scoped to the
LTP process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/stat.h` compatibility wrappers. The file
is built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.
