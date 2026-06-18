<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/getresgid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/getresgid03.c

Purpose: the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program; if not, write to the Free Software Test Name: getresgid03 Test Description: Verify that getresgid() will be successful to get the real, effective and saved user ids after calling process invokes setresgid() to change the effective gid to that of specified user. Expected Result: getresgid() should return with 0 value and the effe

Important APIs/types/functions: includes `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`, `signal.h`, `pwd.h`; touches `getegid`, `getgid`, `getresgid`; defines `setup`, `cleanup`, `main`.

Control flow centers on `setup`, `cleanup`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls.

State and persistence behavior: Runtime state is the real, effective, and saved set-group-ID tuple; legacy tests may temporarily change IDs as root.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdio.h`, `unistd.h`, `sys/types.h`, `errno.h`, `fcntl.h`, `string.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getresgid/getresgid03.c -->
