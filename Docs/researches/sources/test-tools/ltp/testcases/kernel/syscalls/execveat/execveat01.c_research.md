# sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat01.c

Purpose: Checks basic `execveat()` path resolution modes: relative to dirfd, relative to `AT_FDCWD`, absolute path, and `AT_EMPTY_PATH` via an `O_PATH` fd.

Important APIs/types/functions: `execveat`, `SAFE_MKDIR`, `SAFE_CP`, `SAFE_GETCWD`, `SAFE_OPEN(... O_DIRECTORY/O_PATH)`, `AT_FDCWD`, and `AT_EMPTY_PATH`.

Control flow: `setup()` copies the helper into `testdir`, computes an absolute path, and opens directory/file descriptors. Each testcase forks and the child calls `execveat` with one addressing mode.

State and persistence behavior: State consists of the copied helper, directory fd, `O_PATH` fd, and cwd. Successful exec replaces the child image with `execveat_child`.

Dependencies and integration points: Uses `check_execveat()` and a resource helper staged by LTP.

Risks and test signals: Failures isolate dirfd/pathname semantics. Returning from `execveat` is failure because the helper should run.
