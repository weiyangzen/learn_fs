<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace07.c

Purpose: Regression test for commit 814fb7bb7db5 ("x86/fpu: Don't let userspace set bogus xcomp_bv"), or CVE-2017-15537. This bug allowed ptrace(pid, PTRACE_SETREGSET, NT_X86_XSTATE, &iov) to assign a task an invalid FPU state --- specifically, by setting reserved bits in xstate_header.xcomp_bv. This made restoring the FPU registers fail when switching to the task, causing the FPU registers to take on the values from other tasks. To detect the bug, we have a subprocess run a loop checking its xmm0 register for corruption. This detects the case where the FPU state became invalid and the kernel is not restoring the process'

Important APIs/types/functions: includes `tst_test.h`, `errno.h`, `inttypes.h`, `sched.h`, `stdbool.h`, `stdlib.h`, `sys/uio.h`, `sys/wait.h`; exercises `ptrace`; defines `check_regs_loop`, `do_test`; uses flags/constants `PTRACE_ATTACH`, `PTRACE_DETACH`, `PTRACE_GETREGSET`, `PTRACE_SETREGSET`.

Control flow centers on `check_regs_loop`, `do_test`. The `struct tst_test` registration wires `.test_all`, `.forks_child` into the LTP runner. Named case hints include `x86_64`, `linux-git`, `CVE`. Error-path expectations include `EAX`, `EBX`, `ECX`, `EDX`, `EINVAL`, `EIO`, `ENODEV`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `tst_test.h`, `errno.h`, `inttypes.h`, `sched.h`, `stdbool.h`, `stdlib.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TBROK`, `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_ERR`, `TST_RET`, `TST_TEST_TCONF`, `TTERRNO`; checks errno values `EAX`, `EBX`, `ECX`, `EDX`, `EINVAL`, `EIO`, `ENODEV`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace07.c -->
