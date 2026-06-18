<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vfork/vfork01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vfork/vfork01.c

Purpose: verifies a `vfork()` child observes the same process attributes as its parent for effective/real/saved UID and GID, umask, current working directory, and root/current directory inode/device numbers.

Important APIs/types/functions: `run()` captures parent `umask`, `getcwd()`, `SAFE_GETRESUID/GID`, `SAFE_STAT()` for cwd and `/`, then a `vfork()` child compares those values using LTP equality macros and `tst_check_resuid/resgid()`. The child exits with `_exit(0)`.

Control flow/state: parent state is sampled before `vfork`; child performs only comparisons and must not return through parent stack. Parent reaps children and frees the allocated cwd string.

Dependencies/integration: uses LTP UID helpers and marks `.forks_child = 1`. No persistent files are created.

Risks/test signals: `vfork()` shares address space until `_exit`, so adding non-async-safe complex behavior in the child would be risky. Current failures signal attribute inheritance regressions or unexpected cwd/root namespace differences.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vfork/vfork01.c -->
