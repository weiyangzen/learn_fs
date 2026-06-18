<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr02.c

Purpose: Table-driven negative `fgetxattr()` coverage for invalid descriptors, missing attributes, undersized buffers, and bad addresses. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> In the user.* namespace, only regular files and directories can have extended attributes. Otherwise fgetxattr(2) will return -1 and set proper errno. There are 7 test cases: 1. Get attribute from a regular file: - fgetxattr(2) should succeed - checks returned value to be the same as we set 2. Get attribute from a directory: - fgetxattr(2) should succeed - checks returned value to be the same as we set 3. Get attribute from a symlink which points to the regular file: - fgetxattr(2) should succeed - checks returned value to be the same as we set 4. Get attribute from a FIFO: - fgetxattr(2) should return -1 and set errno to ENODATA 5. Get attribute from a char special file: - fgetxattr(2) should return -1 and set errno to ENODATA 6. Get attribute from a block special file: - fgetxattr... The file was read in full for this report (273 lines, 6855 bytes).

Important APIs/types/functions: calls/wrappers: fgetxattr(), open(), getxattr(), SAFE_TOUCH, SAFE_MKDIR, SAFE_SYMLINK, SAFE_MKNOD, SAFE_MALLOC, SAFE_SOCKET, SAFE_BIND, SAFE_OPEN, SAFE_FSETXATTR, SAFE_CLOSE, TST_TEST_TCONF; types/structs: struct test_case, struct sockaddr_un, struct sockaddr, struct tst_test; functions: verify_fgetxattr, setup, cleanup; local macros/constants: XATTR_TEST_KEY, XATTR_TEST_VALUE, XATTR_TEST_VALUE_SIZE, MNTPOINT, OFFSET, FILENAME, DIRNAME, SYMLINK, SYMLINKF, FIFO, CHR, BLK.

Control flow: setup path: setup; exercise path: verify_fgetxattr; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `sys/types.h`, `sys/stat.h`, `sys/sysmacros.h`, `sys/wait.h`, `errno.h`, `fcntl.h`, `unistd.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/socket.h`, `sys/un.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fgetxattr syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ENODATA, EOPNOTSUPP; key constants: O_RDONLY, O_NONBLOCK; harness metadata: .setup, .test, .cleanup, .tcnt, .needs_devfs, .needs_root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fgetxattr/fgetxattr02.c -->
