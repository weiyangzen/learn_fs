# sources/test-tools/ltp/testcases/kernel/syscalls/setxattr/setxattr01.c

## Purpose
Tests for setxattr(2) and make sure setxattr(2) handles error conditions correctly. - EINVAL - any
other flags being set except XATTR_CREATE and XATTR_REPLACE - ENODATA - with XATTR_REPLACE flag set
but the attribute does not exist - ERANGE - create new attr with name length greater than
XATTR_NAME_MAX(255) - E2BIG - create new attr whose value length is greater than
XATTR_SIZE_MAX(65536) - SUCCEED - create new attr whose value length is zero - EEXIST - replace the
attr value without XATTR_REPLACE flag being set - SUCCEED - replace attr value with XATTR_REPLACE
flag being set - ERANGE - create new attr whose key length is zero - EFAULT - create new attr whose
key is NULL.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setxattr`; types `struct test_case`, `struct
tst_test`; safe wrappers `SAFE_SETXATTR`, `SAFE_REMOVEXATTR`, `SAFE_MALLOC`, `SAFE_TOUCH`; harness
APIs `tst_test`, `TEST`, `tst_brk`, `tst_res`, `tst_strerrno`, `tst_get_bad_addr`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.needs_root`. Local functions include `verify_setxattr`, `setup`.

## State and persistence behavior
The test creates temporary filesystem objects under the LTP temporary directory or test mount. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
mount namespace, filesystem type, and kernel version differences affect expected fields; invalid-
address tests can expose architecture-specific fault delivery.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TCONF`, `TTERRNO`, `TERRNO`; expected errno/status values
`EINVAL`, `ENODATA`, `ERANGE`, `E2BIG`, `EEXIST`, `EFAULT`, `EOPNOTSUPP`.
