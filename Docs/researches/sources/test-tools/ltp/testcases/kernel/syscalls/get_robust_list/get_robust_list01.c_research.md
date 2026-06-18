<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_robust_list/get_robust_list01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/get_robust_list/get_robust_list01.c

Purpose: the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program; if not, write to the Free Software Test Name: get_robust_list01 Test Description: Verify that get_robust_list() returns the proper errno for various failure cases Usage: <for command-line> get_robust_list01 [-c n] [-e][-i n] [-I x] [-p x] [-t] where, -c n : Run n copies concurrently. -e : Turn on errno logging. -i n : Execute te

Important APIs/types/functions: includes `sys/types.h`, `sys/syscall.h`, `errno.h`, `stdint.h`, `stdio.h`, `stdlib.h`, `test.h`, `tso_safe_macros.h`; touches `get_robust_list`, `raw syscall path`; defines `setup`, `cleanup`, `main`; uses LTP safe helpers such as `SAFE_SETUID`.

Control flow centers on `setup`, `cleanup`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls. Error-path assertions cover `EFAULT`, `EPERM`, `ESRCH`.

State and persistence behavior: Runtime state is a task robust-futex-list pointer and length; permission and invalid-address paths are part of the kernel ABI surface.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/types.h`, `sys/syscall.h`, `errno.h`, `stdint.h`, `stdio.h`, `stdlib.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TOTAL`. Expected errno values include `EFAULT`, `EPERM`, `ESRCH`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_robust_list/get_robust_list01.c -->
