# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount04.c

## Purpose
This test verifies that statmount() is correctly reading propagation from what mount in current
namespace using STATMOUNT_PROPAGATE_FROM. [Algorithm] - create a mount point - propagate a mounted
folder inside the mount point - run statmount() on the mount point using STATMOUNT_PROPAGATE_FROM -
read results and check propagated_from parameter contains the propagated folder ID.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`, `struct
ltp_statx`, `struct tst_test`, `struct tst_buffers`; constants/macros `STATMOUNT_PROPAGATE_FROM`,
`MS_BIND`, `MS_SHARED`, `MS_SLAVE`, `AT_FDCWD`, `STATX_MNT_ID_UNIQUE`; safe wrappers `SAFE_MKDIR`,
`SAFE_MOUNT`, `SAFE_STATX`, `SAFE_UMOUNT`; harness APIs `TST_EXP_PASS`, `TST_EXP_EQ_LI`,
`tst_is_mounted`, `tst_test`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `run`, `setup`, `cleanup`.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up; creates temporary
filesystem objects under the LTP temporary directory or test mount. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/stat.h` compatibility wrappers. The file
is built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.
