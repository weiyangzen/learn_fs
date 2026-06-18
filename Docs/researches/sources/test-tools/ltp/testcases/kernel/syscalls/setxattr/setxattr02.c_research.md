# sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/setxattr02.c

## Purpose
In the user.* namespace, only regular files and directories can have extended attributes. Otherwise
setxattr(2) will return -1 and set errno to EPERM. - SUCCEED - set attribute to a regular file -
SUCCEED - set attribute to a directory - EEXIST - set attribute to a symlink which points to the
regular file - EPERM - set attribute to a FIFO - EPERM - set attribute to a char special file -
EPERM - set attribute to a block special file - EPERM/SUCCEED - set attribute to a UNIX domain
socket (dc0876b9846d "xattr: support extended attributes on sockets"). Referenced kernel commit ids
include `dc0876b9846d`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `socket`, `setxattr`; types `struct test_case`,
`struct tst_test`; constants/macros `S_IFIFO`, `S_IFCHR`, `S_IFBLK`, `S_IFSOCK`; safe wrappers
`SAFE_SETXATTR`, `SAFE_REMOVEXATTR`, `SAFE_TOUCH`, `SAFE_MKDIR`, `SAFE_SYMLINK`, `SAFE_MKNOD`;
harness APIs `tst_test`, `TEST`, `tst_brk`, `tst_res`, `tst_strerrno`, `tst_kvercmp`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_root`, `.needs_tmpdir`. Local functions include `verify_setxattr`, `setup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, temporary directory support.
The file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TCONF`, `TTERRNO`, `TERRNO`; expected errno/status values
`EPERM`, `EEXIST`, `EOPNOTSUPP`.
