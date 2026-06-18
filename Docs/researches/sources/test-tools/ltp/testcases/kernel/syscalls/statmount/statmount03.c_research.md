# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount03.c

## Purpose
This test verifies that statmount() is correctly reading mount information (mount id, parent mount
id, mount attributes etc.) using STATMOUNT_MNT_BASIC. [Algorithm] - create a mount point - create a
new parent folder inside the mount point and obtain its mount info - create the new "/" mount folder
and obtain its mount info - run statmount() on the mount point using STATMOUNT_MNT_BASIC - read
results and check if mount info are correct.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`, `struct
ltp_statx`, `struct tcase`, `struct tst_test`, `struct tst_buffers`; constants/macros
`STATMOUNT_MNT_BASIC`, `STATX_MNT_ID`, `AT_FDCWD`, `STATX_MNT_ID_UNIQUE`, `MS_PRIVATE`, `MS_SHARED`,
`MS_SLAVE`, `MS_UNBINDABLE`, `MS_BIND`, `MS_REC`; safe wrappers `SAFE_STATX`, `SAFE_MOUNT`,
`SAFE_UMOUNT`, `SAFE_MKDIR`, `SAFE_UNSHARE`; harness APIs `tst_res`, `TST_EXP_PASS`,
`TST_EXP_EQ_LI`, `TST_EXP_EQ_LU`, `tst_is_mounted`, `tst_test`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_tmpdir`. Local functions include `read_mnt_id`, `run`, `setup`, `cleanup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up; creates temporary
filesystem objects under the LTP temporary directory or test mount. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support, `lapi/stat.h`
compatibility wrappers. The file is built by the syscall directory Makefile and executed as part of
the LTP kernel syscall suite.

## Risks and edge cases
Key risks: mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
LTP result macros `TINFO`.
