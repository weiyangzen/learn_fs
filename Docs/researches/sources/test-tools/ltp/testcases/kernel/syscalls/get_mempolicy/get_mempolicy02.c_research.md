<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_mempolicy/get_mempolicy02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/get_mempolicy/get_mempolicy02.c

Purpose: Authors: Takahiro Yasui <takahiro.yasui.mp@hitachi.com> Yumiko Sugita <yumiko.sugita.yf@hitachi.com> Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp> Manas Kumar Nayak <maknayak@in.ibm.com> (original port to the legacy API) Verify that get_mempolicy() returns a proper return errno for failure cases.

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `numa.h`, `numaif.h`, `errno.h`, `tse_numa.h`; touches `get_mempolicy`, `getpagesize`; defines `setup`, `cleanup`, `do_test`.

Control flow centers on `setup`, `cleanup`, `do_test`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.cleanup` into the LTP runner. Error-path assertions cover `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is NUMA policy state attached to a process or mapping, plus an mmap area used for mbind/get_mempolicy checks.

Dependencies and integration points: Depends on libnuma/numaif headers, LTP NUMA capability checks, and helper wrappers for mmap/mbind/set_mempolicy. Direct include dependencies include `config.h`, `tst_test.h`, `numa.h`, `numaif.h`, `errno.h`, `tse_numa.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`, `TST_EXP_FAIL`, `TST_NUMA_MEM`, `TST_TEST_TCONF`. Expected errno values include `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/get_mempolicy/get_mempolicy02.c -->
