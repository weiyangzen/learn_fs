# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx01.c

## Purpose
This code tests the functionality of statx system call. The metadata for normal file are tested
against expected values: - gid - uid - mode - blocks - size - nlink - mnt_id The metadata for device
file are tested against expected values: - MAJOR number - MINOR number.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statx`; types `struct statx`, `struct tcase`,
`struct tst_test`; constants/macros `STATX_MNT_ID`, `AT_FDCWD`, `S_IFMT`, `S_IFBLK`; safe wrappers
`SAFE_FOPEN`, `SAFE_FCLOSE`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `SAFE_MKNOD`,
`SAFE_CLOSE`; harness APIs `tst_test`, `tst_safe_macros`, `tst_safe_stdio`, `tst_res`, `TEST`,
`tst_brk`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_root`, `.needs_devfs`. Local functions include `test_mnt_id`,
`test_normal_file`, `test_device_file`, `run`, `setup`, `cleanup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, device filesystem support,
`lapi/stat.h` compatibility wrappers, `lapi/fcntl.h` compatibility wrappers. The file is built by
the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
mount namespace, filesystem type, and kernel version differences affect expected fields.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TCONF`, `TINFO`, `TTERRNO`, `TERRNO`.
