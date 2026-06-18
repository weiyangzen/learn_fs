<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv202.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv202.c

Purpose: Verify that, preadv2(2) fails and sets errno to 1. EINVAL if iov_len is invalid. 2. EINVAL if the vector count iovcnt is less than zero. 3. EOPNOTSUPP if flag is invalid. 4. EFAULT when attempting to read into an invalid address. 5. EBADF if file descriptor is invalid. 6. EBADF if file descriptor is not open for reading. 7. EISDIR when fd refers to a directory. 8. ESPIPE if fd is associated with a pipe.

Important APIs/types/functions: includes `sys/uio.h`, `unistd.h`, `tst_test.h`, `lapi/uio.h`; exercises `pipe`, `preadv2`, `read`; defines `verify_preadv2`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDONLY`, `O_RDWR`, `O_WRONLY`.

Control flow centers on `verify_preadv2`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test`, `.needs_tmpdir` into the LTP runner. Error-path expectations include `EBADF`, `EFAULT`, `EINVAL`, `EISDIR`, `EOPNOTSUPP`, `ESPIPE`.

State and persistence behavior: Runtime state extends `preadv` with Linux `RWF_*` flags, cache residency, append/nowait behavior, and threaded I/O pressure for NOWAIT coverage.

Dependencies and integration points: Depends on `lapi/uio.h`, preadv2 syscall/libc wrappers, RWF flag support, mounted filesystems, pthread helpers, and cache-drop privileges for NOWAIT testing. Direct include dependencies include `sys/uio.h`, `unistd.h`, `tst_test.h`, `lapi/uio.h`.

Risks and test signals: NOWAIT and HIPRI/RWF behavior varies by filesystem, block device, libc wrapper, and cache pressure, so skips and timing-sensitive failures are expected signals. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EBADF`, `EFAULT`, `EINVAL`, `EISDIR`, `EOPNOTSUPP`, `ESPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv202.c -->
