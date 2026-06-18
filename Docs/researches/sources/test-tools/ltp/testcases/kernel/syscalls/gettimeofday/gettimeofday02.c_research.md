<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettimeofday/gettimeofday02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gettimeofday/gettimeofday02.c

Purpose:  Check if gettimeofday() is monotonous during 10s: - Call gettimeofday() to get a t1 (fist value) - Call it again to get t2, see if t2 < t1, set t2 = t1, repeat for 10 sec

Important APIs/types/functions: includes `stdint.h`, `sys/time.h`, `stdlib.h`, `unistd.h`, `time.h`, `errno.h`, `tst_test.h`, `tst_timer.h`; touches `gettimeofday`, `raw syscall path`; defines `breakout`, `verify_gettimeofday`, `setup`; uses LTP safe helpers such as `SAFE_SIGNAL`.

Control flow centers on `breakout`, `verify_gettimeofday`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is wall-clock time copied from the kernel/vDSO path into timeval buffers.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdint.h`, `sys/time.h`, `stdlib.h`, `unistd.h`, `time.h`, `errno.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettimeofday/gettimeofday02.c -->
