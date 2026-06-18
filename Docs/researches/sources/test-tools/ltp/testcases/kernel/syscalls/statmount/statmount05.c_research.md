# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount05.c

## Purpose
This test verifies STATMOUNT_MNT_ROOT and STATMOUNT_MNT_POINT functionalities of statmount(). In
particular, STATMOUNT_MNT_ROOT will give the mount root (i.e. mount --bind /mnt /bla -> /mnt) and
STATMOUNT_MNT_POINT will give the mount point (i.e. mount --bind /mnt /bla -> /bla). [Algorithm] -
create a mount point - mount a folder inside the mount point - run statmount() on the mounted folder
using STATMOUNT_MNT_ROOT - read results and check if contain the mount root path - run statmount()
on the mounted folder using STATMOUNT_MNT_POINT - read results and check if contain the mount point
path.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`, `struct
ltp_statx`, `struct tst_test`, `struct tst_buffers`; constants/macros `STATMOUNT_MNT_ROOT`,
`STATMOUNT_MNT_POINT`, `MS_BIND`, `AT_FDCWD`, `STATX_MNT_ID_UNIQUE`; safe wrappers `SAFE_MKDIR`,
`SAFE_MOUNT`, `SAFE_STATX`, `SAFE_UMOUNT`; harness APIs `tst_tmpdir`, `tst_res`, `TST_EXP_PASS`,
`TST_EXP_EQ_LI`, `TST_EXP_EQ_STR`, `TST_EXP_POSITIVE`, `tst_tmpdir_genpath`, `tst_is_mounted`,
`tst_test`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `test_mount_root`, `test_mount_point`, `run`, `setup`,
`cleanup`.

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
