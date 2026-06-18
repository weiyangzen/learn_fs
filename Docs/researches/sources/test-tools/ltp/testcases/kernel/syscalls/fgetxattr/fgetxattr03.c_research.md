<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr03.c

Purpose: Regression coverage for `fgetxattr()` buffer-size probing and correct returned value length. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> An empty buffer of size zero can be passed into fgetxattr(2) to return the current size of the named extended attribute. HAVE_SYS_XATTR_H SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (73 lines, 1548 bytes).

Important APIs/types/functions: calls/wrappers: fgetxattr(), SAFE_TOUCH, SAFE_OPEN, SAFE_FSETXATTR, SAFE_CLOSE, TST_TEST_TCONF; types/structs: struct tst_test; functions: verify_fgetxattr, setup, cleanup; local macros/constants: XATTR_TEST_KEY, XATTR_TEST_VALUE, XATTR_TEST_VALUE_SIZE, FILENAME.

Control flow: setup path: setup; exercise path: verify_fgetxattr; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `sys/types.h`, `sys/stat.h`, `sys/wait.h`, `errno.h`, `fcntl.h`, `unistd.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fgetxattr syscall suite; uses the LTP C harness and result macros.

Risks: xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDONLY; harness metadata: .setup, .test_all, .cleanup, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr03.c -->
