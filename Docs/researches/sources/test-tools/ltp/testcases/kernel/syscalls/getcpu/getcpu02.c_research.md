<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/getcpu02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/getcpu02.c

Purpose:  Verify that getcpu(2) fails with EFAULT if cpu_id or node_id points outside the calling process address space.

Important APIs/types/functions: includes `tst_test.h`, `lapi/sched.h`; touches `getcpu`; defines `check_getcpu`; uses LTP safe helpers such as `SAFE_FORK`, `SAFE_WAITPID`.

Control flow centers on `check_getcpu`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.forks_child` into the LTP runner. Error-path assertions cover `EFAULT`.

State and persistence behavior: Runtime state is the current CPU/node reported by the scheduler and optional userspace pointers that receive the values.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/sched.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_EXP_FAIL`. Expected errno values include `EFAULT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/getcpu02.c -->
