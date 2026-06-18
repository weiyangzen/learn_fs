# sources/storage-engines/wiredtiger/test/model/test/common/subprocess.cpp

Purpose: implements `subprocess_helper`, including fork setup, SIGCHLD monitoring, sentinel-file handling, expected abort/exit paths, and parent wait.

Important APIs and functions: static `sentinel_stack`, static `handler_sigchld`, constructor, destructor, `abort_if_child`, `exit_if_child`, and `wait_if_parent`.

Control flow: construction creates a sentinel file in `/tmp`, pushes it on a stack, installs `handler_sigchld`, and forks. The signal handler waits for a child and, if the current sentinel still exists, treats child death as unexpected and fails the parent. Expected child exits remove the sentinel before exiting or killing self. The parent destructor removes the sentinel and restores the previous SIGCHLD handler.

State and persistence: global `sentinel_stack` supports nested helpers. Each helper owns one sentinel path and previous signal action. The only filesystem state is a temporary sentinel file.

Dependencies and integration: uses POSIX `fork`, `wait`, `waitpid`, `sigaction`, `kill`, `getpid`, `exit`, and `abort`; uses `test_util.h` assertions and `create_tmp_file`.

Risks: `handler_sigchld` calls functions from a signal handler that may not be async-signal-safe, but this is test code. Destructor assumes stack top matches the helper's sentinel. `wait_if_parent` only asserts `waitpid` success and does not inspect exit status, relying on sentinel/SIGCHLD for unexpected death.

Test signals: expected abort tests should remove the sentinel and not fail the parent. Unexpected child crashes should trigger `testutil_die`. Nested usage should preserve stack behavior and restore prior handlers.
