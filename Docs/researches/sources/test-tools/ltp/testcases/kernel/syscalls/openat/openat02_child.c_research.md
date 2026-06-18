<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat02_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat02_child.c

Purpose: Companion exec helper for `openat02.c`; it attempts to write through a descriptor number after exec so the parent can verify `O_CLOEXEC` closed the descriptor.

Important APIs/types/functions: includes `stdio.h`, `stdlib.h`, `string.h`, `errno.h`, `unistd.h`; exercises `write`; defines `main`.

Control flow centers on `main`.

State and persistence behavior: Runtime state is filesystem fixtures, directory file descriptors, process cwd handling, file status flags, symlinks, atime/mtime metadata, anonymous temporary files, and child exec inheritance of file descriptors.

Dependencies and integration points: Depends on the LTP safe-file helpers, `openat()` or raw syscall fallback, mount/testcase make rules, helper child binaries, and filesystem support for the specific open flags. Direct include dependencies include `stdio.h`, `stdlib.h`, `string.h`, `errno.h`, `unistd.h`.

Risks and test signals: Open-flag coverage is filesystem and mount-option sensitive, especially `O_TMPFILE`, `O_NOATIME`, `O_DIRECT`, and large-file offsets. Test signals: compile success and consumer test behavior are the available signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat02_child.c -->
