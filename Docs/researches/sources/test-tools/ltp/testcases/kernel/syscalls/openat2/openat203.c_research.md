<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat203.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat203.c

Purpose: Basic :manpage:`openat2(2)` test to check various failures.

Important APIs/types/functions: includes `fcntl.h`, `tst_test.h`, `lapi/openat2.h`; exercises `openat2`, `fcntl`; defines `setup`, `run`; uses flags/constants `AT_FDCWD`, `O_CREAT`, `O_RDONLY`, `O_RDWR`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.needs_tmpdir` into the LTP runner. Named case hints include `invalid-dfd`, `invalid-pathname`, `invalid-flags`, `invalid-mode`, `invalid-resolve`, `invalid-size-zero`, `invalid-size-small`, `invalid-size-big`, `invalid-size-big-with-pad`. Error-path expectations include `E2BIG`, `EBADF`, `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is `struct open_how` resolution policy, directory file descriptors, symlink/magic-link fixtures, mount boundaries, and file descriptors returned by the raw `openat2` syscall.

Dependencies and integration points: Depends on `lapi/openat2.h`, raw syscall availability, `struct open_how`, root/mount fixtures for resolution flags, and Linux 5.6-era openat2 semantics. Direct include dependencies include `fcntl.h`, `tst_test.h`, `lapi/openat2.h`.

Risks and test signals: Resolution-constraint failures depend on exact kernel `openat2()` semantics and fixture layout; unsupported kernels must skip rather than fail. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `E2BIG`, `EBADF`, `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat203.c -->
