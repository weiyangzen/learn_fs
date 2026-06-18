<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/fsetxattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/fsetxattr02.c

Purpose: Negative `fsetxattr()` coverage for invalid descriptors, flags, namespace/name errors, bad address, and size constraints. Source notes: Author: Rafael David Tinoco <rafael.tinoco@linaro.org> \ Verify basic fsetxattr(2) syscall functionality: - Set attribute to a regular file, fsetxattr(2) should succeed. - Set attribute to a directory, fsetxattr(2) should succeed. - Set attribute to a symlink which points to the regular file, fsetxattr(2) should return -1 and set errno to EEXIST. - Set attribute to a FIFO, fsetxattr(2) should return -1 and set errno to EPERM. - Set attribute to a char special file, fsetxattr(2) should return -1 and set errno to EPERM. - Set attribute to a block special file, fsetxattr(2) should return -1 and set errno to EPERM. - Set attribute to a UNIX domain socket, fsetxattr(2) should return -1 and set errno to EPERM on kernels < 7.1.0. On kernel 7.1.0+ (dc0876b9846d "xattr: support extended attributes on sockets"), returns 0 (success) as sockets no... The file was read in full for this report (276 lines, 6827 bytes).

Important APIs/types/functions: calls/wrappers: fsetxattr(), open(), SAFE_FSETXATTR, SAFE_FREMOVEXATTR, SAFE_TOUCH, SAFE_MKDIR, SAFE_SYMLINK, SAFE_MKNOD, SAFE_OPEN, SAFE_SOCKET, SAFE_BIND, SAFE_CLOSE, TST_TEST_TCONF; types/structs: struct test_case, struct sockaddr_un, struct sockaddr, struct tst_test; functions: verify_fsetxattr, setup, cleanup; local macros/constants: XATTR_TEST_KEY, XATTR_TEST_VALUE, XATTR_TEST_VALUE_SIZE, MNTPOINT, OFFSET, FILENAME, DIRNAME, SYMLINK, FIFO, CHR, BLK, SOCK.

Control flow: setup path: setup; exercise path: verify_fsetxattr; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, UID/capability-sensitive kernel state, temporary mount/test filesystem state, filesystem extended attributes. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `config.h`, `sys/types.h`, `sys/stat.h`, `sys/sysmacros.h`, `sys/wait.h`, `errno.h`, `fcntl.h`, `unistd.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/socket.h`, `sys/un.h`, `sys/xattr.h`, `tst_test.h`; integrates with the LTP fsetxattr syscall suite; uses the LTP C harness and result macros; declares kernel configuration requirements.

Risks: requires root/capability-sensitive behavior; xattr namespace and filesystem support vary by mount options.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EEXIST, EPERM, EOPNOTSUPP; key constants: O_RDONLY, O_NONBLOCK; harness metadata: .setup, .test, .cleanup, .tcnt, .needs_devfs, .needs_root, .needs_kconfigs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsetxattr/fsetxattr02.c -->
