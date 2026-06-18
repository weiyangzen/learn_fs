<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/vhangup02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/vhangup02.c

Purpose: verifies privileged `vhangup()` can succeed from a child process that has created a new session.

Important APIs/types/functions: `run()` forks; the child calls `setsid()` and then `tst_syscall(__NR_vhangup)`, reporting pass if the syscall does not return `-1`.

Control flow/state: the parent waits while the child isolates itself as a session leader before invoking the syscall. There is no file or terminal fixture beyond the process session state.

Dependencies/integration: root is required. The test uses the LTP raw syscall path and child forking metadata.

Risks/test signals: behavior can depend on available controlling terminal/session context in the test environment. A failure with errno is a direct signal that privileged `vhangup()` was rejected or unsupported.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vhangup/vhangup02.c -->
