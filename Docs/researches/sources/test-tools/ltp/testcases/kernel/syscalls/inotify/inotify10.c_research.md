<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify10.c

Purpose: Started by Amir Goldstein <amir73il@gmail.com> Check that event is reported to watching parent and watching child based on their interest. Test case #3 is a regression test for commit fecc4559780d that fixes a bug introduced in kernel v5.9: fecc4559780d ("fsnotify: fix events reported to watching parent and child").

Important APIs/types/functions: includes `config.h`, `errno.h`, `string.h`, `tst_test.h`, `inotify.h`; defines `verify_inotify`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_CHMOD`, `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MKDIR`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT`, `SAFE_READ`.

Control flow centers on `verify_inotify`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test`, `.tcnt` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `errno.h`, `string.h`, `tst_test.h`, `inotify.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify10.c -->
