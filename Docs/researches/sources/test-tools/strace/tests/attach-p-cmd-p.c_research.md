<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/attach-p-cmd-p.c -->
## sources/test-tools/strace/tests/attach-p-cmd-p.c

Purpose: `-p` side companion for `attach-p-cmd`, coordinating with a command process then emitting a delayed trace line.

Important APIs/types/functions: Uses `mkdir/rmdir` lock handoff, pid file reading, `kill(pid, 0)` polling, `unlink`, `nanosleep`, `chdir`, and constants from `attach-p-cmd.h`.

Control flow: Creates lockdir, waits until peer removes it and recreates/removes it for cleanup, reads peer pid, waits for peer termination, sleeps briefly, then attempts `chdir("attach-p-cmd.test -p")` and prints pid-prefixed output.

State and persistence: Creates/removes `attach-p-cmd.test-lock` and removes `attach-p-cmd.test-pid`.

Dependencies and integration: Paired with `attach-p-cmd-cmd.c`; validates strace attaching to an existing process while also running a command.

Risks: Uses busy loops over filesystem and process liveness, so stale files or permission issues can deadlock/fail.

Test signals: Expected output appears only after peer termination and includes failed `chdir("attach-p-cmd.test -p")`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/attach-p-cmd-p.c -->
