# sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat02.c

Purpose: Checks `execveat()` error handling for bad fd, invalid flags, symlink nofollow, and relative pathname under a non-directory fd.

Important APIs/types/functions: `execveat`, `SAFE_SYMLINK`, `SAFE_OPEN(... O_PATH)`, `AT_EMPTY_PATH`, `AT_SYMLINK_NOFOLLOW`, `TST_ERR`, and a table of expected errnos.

Control flow: `setup()` creates a directory, copies the errno helper, builds absolute/symlink paths, and opens the target file with `O_PATH`. Each forked child calls `execveat` and compares errno.

State and persistence behavior: Filesystem state includes a copied executable and symlink. Descriptor state includes a deliberate bad fd and an `O_PATH` fd to a regular file.

Dependencies and integration points: Integrated with `execveat_errno.c`, which should not run in any testcase.

Risks and test signals: If a case unexpectedly executes, the helper reports failure. SELinux or filesystem behavior could alter some errno paths, but the cases target kernel API validation.
