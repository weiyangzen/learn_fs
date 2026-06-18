<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify11.c

Purpose: Started by Amir Goldstein <amir73il@gmail.com> based on reproducer from Ivan Delalande <colona@arista.com> Test opening files after receiving IN_DELETE. Kernel v5.13 has a regression allowing files to be open after IN_DELETE. The problem has been fixed by commit: a37d9a17f099 ("fsnotify: invalidate dcache before IN_DELETE event").

Important APIs/types/functions: includes `config.h`, `stdio.h`, `unistd.h`, `fcntl.h`, `signal.h`, `sys/wait.h`, `tst_test.h`, `tst_safe_macros.h`; defines `churn`, `verify_inotify`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_FORK`, `SAFE_KILL`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT`, `SAFE_READ`, `SAFE_UNLINK`.

Control flow centers on `churn`, `verify_inotify`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.forks_child`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `unistd.h`, `fcntl.h`, `signal.h`, `sys/wait.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify11.c -->
