<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv02.c

Purpose: - EINVAL when iov_len is invalid. - EINVAL when the vector count iovcnt is less than zero. - EINVAL when offset is negative. - EFAULT when attempts to read into a invalid address. - EBADF when file descriptor is invalid. - EBADF when file descriptor is not open for reading. - EISDIR when fd refers to a directory. - ESPIPE when fd is associated with a pipe.

Important APIs/types/functions: includes `sys/uio.h`, `unistd.h`, `tst_test.h`, `lapi/uio.h`; exercises `pipe`, `preadv`, `read`; defines `verify_preadv`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDONLY`, `O_RDWR`, `O_WRONLY`.

Control flow centers on `verify_preadv`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test`, `.needs_tmpdir` into the LTP runner. Error-path expectations include `EBADF`, `EFAULT`, `EINVAL`, `EISDIR`, `ESPIPE`.

State and persistence behavior: Runtime state is vector I/O buffers, file content, offsets, and descriptor position, including error-path descriptors and direct-I/O alignment where tested.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/uio.h`, `unistd.h`, `tst_test.h`, `lapi/uio.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EBADF`, `EFAULT`, `EINVAL`, `EISDIR`, `ESPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv02.c -->
