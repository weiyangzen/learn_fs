# sources/test-tools/fio/os/windows/posix/include/sys/wait.h

Purpose: minimal wait-status compatibility header for Windows.

Important APIs/types: defines `WIFSIGNALED`, `WIFEXITED`, `WTERMSIG`, and `WEXITSTATUS` as zero-valued macros, `WNOHANG` as `1`, and declares `waitpid()`.

Control flow and state: `posix.c` implements `waitpid()` as an `ENOSYS` stub.

Dependencies and integration: lets Unix-oriented process code compile on Windows while fio uses alternate child-process handling where needed.

Risks: wait status macros never report success, signals, or exit status. Any logic relying on real wait semantics will misbehave.

Test signals: Windows process code should avoid depending on `waitpid()`; compile paths are the primary signal.
