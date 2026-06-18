<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify04.c

Purpose: Ngie Cooper, April 2012 Test for inotify IN_DELETE_SELF event. [Algorithm] This testcase creates a temporary directory, then add watches to a predefined file and subdirectory, and delete the file and directory to ensure that the IN_DELETE_SELF event is captured properly. Because of how the inotify(7) API is designed, we also need to catch the IN_ATTRIB and IN_IGNORED events.

Important APIs/types/functions: includes `config.h`, `errno.h`, `string.h`, `tst_test.h`, `inotify.h`; touches `inotify_rm_watch`; defines `cleanup`, `setup`, `verify_inotify`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_MKDIR`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT`, `SAFE_READ`, `SAFE_RMDIR`, `SAFE_UNLINK`.

Control flow centers on `cleanup`, `setup`, `verify_inotify`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `errno.h`, `string.h`, `tst_test.h`, `inotify.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify04.c -->
