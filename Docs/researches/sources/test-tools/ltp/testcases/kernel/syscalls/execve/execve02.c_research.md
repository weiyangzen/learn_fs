# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve02.c

Purpose: Verifies `execve()` returns `EACCES` when an unprivileged effective user attempts to execute a root-owned helper lacking execute permission for others.

Important APIs/types/functions: `SAFE_CHMOD`, `SAFE_GETPWNAM("nobody")`, `SAFE_SETEUID`, `execve(TEST_APP, argv, environ)`, and `.needs_root`/`.resource_files`.

Control flow: `setup()` chmods `execve_child` to 0700 and records nobody's uid. The forked child switches euid to nobody, calls `execve`, expects failure, and checks `TST_ERR == EACCES`.

State and persistence behavior: State includes helper file mode bits and the child's effective uid. The parent environment is inherited so the helper could reinitialize if accidentally executed.

Dependencies and integration points: Uses a staged resource helper and root privileges to change credentials safely.

Risks and test signals: If permission checks regress, exec may succeed and the helper reports that it should not have run. Wrong errno also fails.
