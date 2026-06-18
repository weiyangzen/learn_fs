<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify.h

Purpose: Common inotify wrapper header that maps raw inotify syscalls and turns unsupported kernels or watch failures into LTP results.

Important APIs/types/functions: includes `lapi/syscalls.h`; touches `inotify_init`, `inotify_add_watch`, `raw syscall path`; defines `safe_myinotify_init`, `safe_myinotify_watch`; uses LTP safe helpers such as `SAFE_MYINOTIFY_ADD_WATCH`, `SAFE_MYINOTIFY_INIT`, `SAFE_MYINOTIFY_INIT1`.

Control flow centers on `safe_myinotify_init`, `safe_myinotify_watch`. Error-path assertions cover `ENOSYS`.

State and persistence behavior: Runtime state is inotify instances, watch descriptors, queued struct inotify_event records, and filesystem objects being watched or mutated.

Dependencies and integration points: Depends on inotify syscall wrappers, sys/inotify.h constants, temporary filesystem fixtures, and sometimes mounts, overlayfs, checkpoints, or fsnotify race helpers. Direct include dependencies include `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TCONF`. Expected errno values include `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify/inotify.h -->
