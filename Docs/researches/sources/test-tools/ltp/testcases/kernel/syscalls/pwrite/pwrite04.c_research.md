<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite04.c

Purpose: ported from SPIE, section2/filesuite/pread_pwrite.c, by Airong Zhang Test the pwrite() system call with O_APPEND. Writing 2k data to the file, close it and reopen it with O_APPEND. POSIX requires that opening a file with the O_APPEND flag should have no effect on the location at which pwrite() writes data. However, on Linux, if a file is opened with O_APPEND, pwrite() appends data to the end of the file, regardless of the value of offset.

Important APIs/types/functions: includes `stdlib.h`, `inttypes.h`, `tst_test.h`, `tst_safe_prw.h`; exercises `pwrite`, `lseek`; defines `l_seek`, `verify_pwrite`, `setup`, `cleanup`; uses flags/constants `O_APPEND`, `O_CREAT`, `O_RDWR`, `O_TRUNC`.

Control flow centers on `l_seek`, `verify_pwrite`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is file content written at explicit offsets, descriptor offsets that should not move for `pwrite()`, and Linux `O_APPEND` behavior.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdlib.h`, `inttypes.h`, `tst_test.h`, `tst_safe_prw.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite04.c -->
