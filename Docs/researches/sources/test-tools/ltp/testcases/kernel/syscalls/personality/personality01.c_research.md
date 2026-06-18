<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/personality/personality01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/personality/personality01.c

Purpose: 03/2001 - Written by Wayne Boyer Tries to set different personalities. We set the personality in a child process since it's not guaranteed that we can set it back in some cases. I.e. PER_LINUX32 cannot be unset on some 64 bit archs.

Important APIs/types/functions: includes `tst_test.h`, `lapi/personality.h`; exercises `personality`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is the process execution-domain/personality word, including architecture-specific flags that must be restored after each test.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/personality.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_EXPR`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/personality/personality01.c -->
