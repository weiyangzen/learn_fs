<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify05.c

Purpose:  Check that inotify overflow event is properly generated.

Important APIs/types/functions: includes `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `fcntl.h`, `errno.h`, `string.h`, `sys/syscall.h`; touches `getpid`, `inotify_rm_watch`; defines `verify_inotify`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FILE_SCANF`, `SAFE_LSEEK`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT1`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_WRITE`.

Control flow centers on `verify_inotify`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `fcntl.h`, `errno.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify05.c -->
