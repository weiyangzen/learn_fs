<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpriority/getpriority02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpriority/getpriority02.c

Purpose: Ported to LTP: Wayne Boyer 11/2016 Modified by Guangwen Feng <fenggw-fnst@cn.fujitsu.com> Verify that, 1) getpriority(2) fails with -1 and sets errno to EINVAL if 'which' argument was not one of PRIO_PROCESS, PRIO_PGRP, or PRIO_USER. 2) getpriority(2) fails with -1 and sets errno to ESRCH if no process was located for 'which' and 'who' arguments.

Important APIs/types/functions: includes `errno.h`, `sys/resource.h`, `sys/time.h`, `tst_test.h`; touches `getpriority`; defines `verify_getpriority`.

Control flow centers on `verify_getpriority`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `EINVAL`, `ESRCH`.

State and persistence behavior: Runtime state is scheduler nice/priority lookup for process, group, and user selectors.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `sys/resource.h`, `sys/time.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`. Expected errno values include `EINVAL`, `ESRCH`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpriority/getpriority02.c -->
