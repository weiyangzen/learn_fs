<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify06.c

Purpose:  Test for inotify mark destruction race. Kernels prior to 4.2 have a race when inode is being deleted while inotify group watching that inode is being torn down. When the race is hit, the kernel crashes or loops. The problem has been fixed by commit: 8f2f3eb59dff ("fsnotify: fix oops in fsnotify_clear_marks_by_group_flags()").

Important APIs/types/functions: includes `config.h`, `stdio.h`, `unistd.h`, `stdlib.h`, `fcntl.h`, `time.h`, `signal.h`, `sys/time.h`; defines `setup`, `verify_inotify`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_FILE_SCANF`, `SAFE_FORK`, `SAFE_KILL`, `SAFE_MYINOTIFY_INIT1`, `SAFE_OPEN`, `SAFE_UNLINK`.

Control flow centers on `setup`, `verify_inotify`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.needs_tmpdir`, `.forks_child`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `unistd.h`, `stdlib.h`, `fcntl.h`, `time.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify06.c -->
