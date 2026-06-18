<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv03.c

Purpose: Check the basic functionality of the preadv(2) for the file opened with O_DIRECT in all filesystem. preadv(2) should succeed to read the expected content of data and after reading the file, the file offset is not changed.

Important APIs/types/functions: includes `stdlib.h`, `string.h`, `sys/uio.h`, `sys/ioctl.h`, `sys/mount.h`, `tst_test.h`, `lapi/uio.h`; exercises `preadv`, `mount`, `read`, `ioctl`; defines `verify_direct_preadv`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_DIRECT`, `O_RDWR`.

Control flow centers on `verify_direct_preadv`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test`, `.mntpoint`, `.mount_device`, `.all_filesystems`, `.skip_filesystems` into the LTP runner. Named case hints include `tmpfs`.

State and persistence behavior: Runtime state is vector I/O buffers, file content, offsets, and descriptor position, including error-path descriptors and direct-I/O alignment where tested.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdlib.h`, `string.h`, `sys/uio.h`, `sys/ioctl.h`, `sys/mount.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TFAIL`, `TINFO`, `TPASS`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv03.c -->
