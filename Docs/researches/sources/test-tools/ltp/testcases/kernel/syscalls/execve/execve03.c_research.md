# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve03.c

Purpose: Covers multiple `execve()` errno cases: `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `EFAULT`, `EACCES`, and `ENOEXEC`.

Important APIs/types/functions: `execve`, `SAFE_GETPWNAM`, `SAFE_SETGID`, `SAFE_GETCWD`, `SAFE_CREAT`, `tst_get_bad_addr`, and a table-driven `struct tcase`.

Control flow: `setup()` creates paths and files for each error condition, including a non-executable file and a zero-length executable file. Each testcase calls `execve(tc->tname, argv, NULL)` and compares `TST_ERR` to the expected errno.

State and persistence behavior: Temporary filesystem entries and a bad userspace pointer define the test state. No successful exec should occur.

Dependencies and integration points: Requires root and a tmpdir because it changes gid and creates controlled permission/path states.

Risks and test signals: Path construction and permission setup must match kernel checks; ordering matters because `ENOTDIR` is produced by appending a component beneath a regular file.
