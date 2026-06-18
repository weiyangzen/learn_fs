<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat.h

Purpose: Compatibility header for `openat` syscall tests; it provides a raw `tst_syscall(__NR_openat, ...)` fallback when libc does not expose `openat()`.

Important APIs/types/functions: includes `sys/types.h`, `config.h`, `lapi/syscalls.h`; defines `openat`; touches `openat`, `write`, `raw syscall path`.

Control flow: this file is consumed at compile time by sibling tests; any inline or fallback functions normalize missing libc/kernel interfaces before the test bodies run.

State and persistence behavior: Runtime state is filesystem fixtures, directory file descriptors, process cwd handling, file status flags, symlinks, atime/mtime metadata, anonymous temporary files, and child exec inheritance of file descriptors.

Dependencies and integration points: Depends on the LTP safe-file helpers, `openat()` or raw syscall fallback, mount/testcase make rules, helper child binaries, and filesystem support for the specific open flags. Direct include dependencies include `sys/types.h`, `config.h`, `lapi/syscalls.h`.

Risks and test signals: fallback wrappers must match the real syscall ABI exactly; otherwise sibling tests can pass compile but exercise the wrong argument layout. Signals are compile success and correct behavior in the consuming tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat.h -->
