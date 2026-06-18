<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syscall/syscall01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/syscall/syscall01.c

Purpose: 01/02/2003 Port to LTP avenkat@us.ibm.com 06/30/2001 Port to Linux nsharoff@us.ibm.com Basic test for syscall(). Compare raw get{g,p,u}id results with their glibc wrappers.

Important APIs/types/functions: includes `unistd.h`, `sys/syscall.h`, `sys/types.h`, `tst_test.h`, `lapi/syscalls.h`; exercises `syscall`, `raw syscall path`; defines `verify_getpid`, `verify_getuid`, `verify_getgid`, `verify_syscall`.

Control flow centers on `verify_getpid`, `verify_getuid`, `verify_getgid`, `verify_syscall`. The `struct tst_test` registration wires `.test`, `.tcnt` into the runner.

State and persistence behavior: Runtime state is the raw syscall ABI dispatch path and errno propagation for syscall numbers and arguments selected by the test.

Dependencies and integration points: Depends on libc `syscall()`, LTP errno/result helpers, and syscall numbers present for the target architecture. Direct include dependencies include `unistd.h`, `sys/syscall.h`, `sys/types.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syscall/syscall01.c -->
