<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ppoll/ppoll01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ppoll/ppoll01.c

Purpose: Author(s): Takahiro Yasui <takahiro.yasui.mp@hitachi.com>, Yumiko Sugita <yumiko.sugita.yf@hitachi.com>, Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp> Older versions of glibc don't publish this constant's value. test type (enum)

Important APIs/types/functions: includes `errno.h`, `poll.h`, `signal.h`, `stdlib.h`, `sys/types.h`, `sys/wait.h`, `tso_signal.h`, `time64_variants.h`; exercises `poll`, `ppoll`, `raw syscall path`; defines `libc_ppoll`, `sys_ppoll`, `sys_ppoll_time64`, `sighandler`, `setup`, `cleanup`, `do_test`; uses flags/constants `O_CREAT`, `O_RDWR`, `POLLIN`, `POLLNVAL`, `POLLOUT`, `POLLPRI`, `POLLRDHUP`.

Control flow centers on `libc_ppoll`, `sys_ppoll`, `sys_ppoll_time64`, `sighandler`, `setup`, `cleanup`, `do_test`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.test_variants`, `.setup`, `.cleanup`, `.forks_child`, `.needs_tmpdir` into the LTP runner. Named case hints include `x`, `NORMAL`, `MASK_SIGNAL`, `TIMEOUT`, `FD_ALREADY_CLOSED`, `SEND_SIGINT`, `SEND_SIGINT_RACE_TEST`, `INVALID_NFDS`, `INVALID_FDS`. Error-path expectations include `EBADF`, `EFAULT`, `EINTR`, `EINVAL`, `ENOMEM`.

State and persistence behavior: Runtime state is `struct pollfd` arrays, optional signal masks atomically installed by `ppoll`, timespec variants, and signal-generator children.

Dependencies and integration points: Depends on time64 variants, raw ppoll syscall numbers, signal-generator helpers, pollfd fixtures, and sigset/timespec ABI conversion. Direct include dependencies include `errno.h`, `poll.h`, `signal.h`, `stdlib.h`, `sys/types.h`, `sys/wait.h`.

Risks and test signals: Signal and timeout races are intentional; variants must preserve sigset and timespec ABI handling across libc, old syscall, and time64 syscall paths. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_LIBC_TIMESPEC`; checks errno values `EBADF`, `EFAULT`, `EINTR`, `EINVAL`, `ENOMEM`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ppoll/ppoll01.c -->
