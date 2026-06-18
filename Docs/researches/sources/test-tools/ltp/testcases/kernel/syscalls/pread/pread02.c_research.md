<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pread/pread02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pread/pread02.c

Purpose: 07/2001 Ported by Wayne Boyer Tests basic error handling of the pread syscall. - ESPIPE when attempted to read from an unnamed pipe - EINVAL if the specified offset position was invalid - EISDIR when fd refers to a directory

Important APIs/types/functions: includes `fcntl.h`, `stdlib.h`, `tst_test.h`; exercises `pipe`, `pread`, `read`, `fcntl`; defines `verify_pread`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDONLY`, `O_RDWR`.

Control flow centers on `verify_pread`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.needs_tmpdir`, `.setup`, `.cleanup`, `.test` into the LTP runner. Error-path expectations include `EINVAL`, `EISDIR`, `ESPIPE`.

State and persistence behavior: Runtime state is file content and descriptor offsets: `pread()` must read from supplied offsets without changing the current file position.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `fcntl.h`, `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL2`; checks errno values `EINVAL`, `EISDIR`, `ESPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pread/pread02.c -->
