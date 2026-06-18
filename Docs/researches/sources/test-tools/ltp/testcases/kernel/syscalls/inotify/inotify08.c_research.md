<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify08.c

Purpose:  Check that inotify work for an overlayfs file after copy up and drop caches. An inotify watch pins the file inode in cache, but not the dentry. The watch will not report events on the file if overlayfs does not obtain the pinned inode to the new allocated dentry after drop caches. The problem has been fixed by commit: 764baba80168 ("ovl: hash non-dir by lower inode for fsnotify"). [Algorithm] Add watch on an overlayfs lower file then chmod file and drop dentry and inode caches. Execute operations on file and expec

Important APIs/types/functions: includes `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `sys/sysmacros.h`, `fcntl.h`, `errno.h`, `string.h`; touches `inotify_rm_watch`; defines `verify_inotify`, `setup`, `cleanup`; uses LTP safe helpers such as `SAFE_CHMOD`, `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MOUNT_OVERLAY`, `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT1`, `SAFE_READ`, `SAFE_READ_ANY_EAGAIN`.

Control flow centers on `verify_inotify`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.mount_device`, `.needs_overlay`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `config.h`, `stdio.h`, `sys/stat.h`, `sys/types.h`, `sys/sysmacros.h`, `fcntl.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify08.c -->
