<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open02.c

Purpose: Tests basic error handling of the pidfd_open syscall. - ESRCH the process specified by pid does not exist - EINVAL pid is not valid - EINVAL flags is not valid

Important APIs/types/functions: includes `tst_test.h`, `lapi/pidfd.h`; exercises `pidfd_open`; defines `setup`, `run`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup` into the LTP runner. Named case hints include `expired pid`, `invalid pid`, `invalid flags`. Error-path expectations include `EINVAL`, `ESRCH`.

State and persistence behavior: Runtime state is live process identity represented as pidfds, polling state when children exit, and error handling for invalid PIDs or flags.

Dependencies and integration points: Depends on pidfd syscall wrappers, fork/wait/poll helpers, kernel pidfd support, and process lifetime handling. Direct include dependencies include `tst_test.h`, `lapi/pidfd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL2`; checks errno values `EINVAL`, `ESRCH`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open02.c -->
