<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/time/time01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/time/time01.c

Purpose: Basic test for the time(2) system call. Verify that time(2) returns the value of time in seconds since the Epoch and stores this value in the memory pointed to by the parameter.

Important APIs/types/functions: includes `time.h`, `errno.h`, `tst_test.h`; exercises `time`; defines `verify_time`.

Control flow centers on `verify_time`. The `struct tst_test` registration wires `.test`, `.tcnt` into the runner.

State and persistence behavior: Runtime state is the wall-clock seconds value returned by `time()` and optionally copied into a caller-provided pointer.

Dependencies and integration points: Depends on libc `time()` and a valid or invalid userspace pointer according to the case. Direct include dependencies include `time.h`, `errno.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/time/time01.c -->
