<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/getcpu01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/getcpu01.c

Purpose:  The test process is affined to a CPU. It then calls getcpu and checks that the CPU and node (if supported) match the expected values.

Important APIs/types/functions: includes `dirent.h`, `errno.h`, `stdio.h`, `stdlib.h`, `sys/types.h`, `tst_test.h`, `lapi/cpuset.h`, `lapi/sched.h`; touches `getcpu`; defines `max_cpuid`, `set_cpu_affinity`, `get_nodeid`, `run`.

Control flow centers on `max_cpuid`, `set_cpu_affinity`, `get_nodeid`, `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner. Error-path assertions cover `EINVAL`.

State and persistence behavior: Runtime state is the current CPU/node reported by the scheduler and optional userspace pointers that receive the values.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `dirent.h`, `errno.h`, `stdio.h`, `stdlib.h`, `sys/types.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`. Expected errno values include `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcpu/getcpu01.c -->
