<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify09.c

Purpose: Chnaged to use fzsync library by Cyril Hrubis <chrubis@suse.cz> Test for inotify mark connector destruction race. Kernels prior to 4.17 have a race when the last fsnotify mark on the inode is being deleted while another process reports event happening on that inode. When the race is hit, the kernel crashes or loops. The problem has been fixed by commit: d90a10e2444b ("fsnotify: Fix fsnotify_mark_connector race").

Important APIs/types/functions: includes `config.h`, `stdio.h`, `unistd.h`, `stdlib.h`, `fcntl.h`, `time.h`, `signal.h`, `sys/time.h`; touches `inotify_rm_watch`; defines `setup`, `cleanup`, `verify_inotify`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_LSEEK`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT1`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ANY`.

Control flow centers on `setup`, `cleanup`, `verify_inotify`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `unistd.h`, `stdlib.h`, `fcntl.h`, `time.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify09.c -->
