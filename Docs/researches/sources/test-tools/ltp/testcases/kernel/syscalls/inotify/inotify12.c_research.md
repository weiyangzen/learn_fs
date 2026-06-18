<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify12.c

Purpose:  Test special inotify mask flags. Regression test for kernel commit: a32e697cda27 ("inotify: show inotify mask flags in proc fdinfo").

Important APIs/types/functions: includes `config.h`, `stdio.h`, `unistd.h`, `fcntl.h`, `signal.h`, `sys/wait.h`, `tst_test.h`, `tst_safe_macros.h`; touches `getpid`; defines `verify_inotify`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT1`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_UNLINK`, `SAFE_WRITE`.

Control flow centers on `verify_inotify`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.cleanup`, `.test`, `.tcnt` into the LTP runner. Error-path assertions cover `EAGAIN`.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `unistd.h`, `fcntl.h`, `signal.h`, `sys/wait.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`. Expected errno values include `EAGAIN`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify12.c -->
